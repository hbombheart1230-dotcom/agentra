"""Behavior-preserving Reporter R-4 implementation bodies moved from ``libs/reporting/trade_report_markdown_strategy_memory.py``.

Each function keeps its original body except that every former facade module global is qualified at its use
site as ``facade.NAME`` (explicit injected module, no getattr fallback, no entry-time capture), so use-time lookup
and monkeypatching match the original module-level resolution. This owner never imports the facade.
"""
from __future__ import annotations


def build_memory_application_r4_impl(report, *, deps, facade):
    _as_dict = deps['as_dict']
    _badge = deps['badge']
    _listify = deps['listify']
    _memory_layers_text = deps['memory_layers_text']
    _metadata_value = deps['metadata_value']
    _monitor_delta_interpretation = deps['monitor_delta_interpretation']
    _monitor_phase_line = deps['monitor_phase_line']
    _num_opt = deps['num_opt']
    _playbook_label = deps['playbook_label']
    _policy_phase_line = deps['policy_phase_line']
    _policy_source_label = deps['policy_source_label']
    _reason_summary_line = deps['reason_summary_line']
    _resolve_prompt_proven_surface = deps['resolve_prompt_proven_surface']
    _same_policy_snapshot = deps['same_policy_snapshot']
    _scanner_phase_line = deps['scanner_phase_line']
    memory_app = _as_dict(report.get('memory_application_surface'))
    if not memory_app:
        return []
    memory_surface = _as_dict(report.get('memory_surface'))
    prompt_surface = _resolve_prompt_proven_surface(memory_surface) if memory_surface else {}
    prompt_policy = _as_dict(prompt_surface.get('commander_memory_policy'))
    latest_policy = _as_dict(memory_surface.get('commander_memory_policy'))
    scanner = _as_dict(memory_app.get('scanner_memory_bias'))
    monitor = _as_dict(memory_app.get('monitor_memory_bias'))
    lines: List[str] = []
    lines.append(f"- {_badge('적용 결과', '#b45309')} 메모리 영향은 전략가 입력, 스캐너 적용, 모니터 적용, 최신 커맨더 상태 순서로 분리했습니다.")
    if prompt_policy:
        lines.append(_policy_phase_line('전략가 입력 시점', prompt_policy))
    else:
        lines.append('- [전략가 입력 시점] 지휘관 메모리 정책은 전략가 프롬프트에서 직접 확인되지 않았습니다.')
    if scanner:
        lines.append(_scanner_phase_line(scanner))
    else:
        lines.append('- [스캐너 적용 시점] 스캐너 메모리 적용 trace가 없습니다.')
    if monitor:
        lines.append(_monitor_phase_line(monitor))
    else:
        lines.append('- [모니터 적용 시점] 모니터 메모리 적용 trace가 없습니다.')
    if latest_policy:
        lines.append(_policy_phase_line('최신 커맨더 상태', latest_policy))
        if prompt_policy and (not _same_policy_snapshot(prompt_policy, latest_policy)):
            lines.append('- [시점 차이] 최신 커맨더 상태는 전략가 프롬프트 이후 실행/복원 기준이라 전략가 입력 시점과 다를 수 있습니다.')
    else:
        lines.append('- [최신 커맨더 상태] 리포트에서 최신 커맨더 메모리 정책을 확인하지 못했습니다.')
    lines.append('- [적용 해석] 전략가 입력 시점의 비활성 여부보다 실제 매매 영향은 스캐너/모니터 적용 시점 라인을 우선 봅니다.')
    if scanner.get('captured'):
        active_layers = _memory_layers_text(scanner.get('active_layers'))
        state = '실제 후보 점수에 적용된 상태' if scanner.get('applied') else '요약만 기록된 상태'
        lines.append(f'- 스캐너 메모리 가중치는 {state}이며, 실제 반영 레이어는 {active_layers}입니다.')
        deltas = _as_dict(scanner.get('source_weight_delta'))
        if deltas:
            ordered = [f'{key} {float(val):+0.3f}' for key, val in deltas.items() if _num_opt(val) is not None]
            if ordered:
                lines.append(f"- 스캐너 소스 가중치 변화는 {', '.join(ordered)}입니다.")
        else:
            lines.append('- 스캐너 쪽은 소스 가중치 변화 상세가 남지 않아, 후보별 가감점만 확인됩니다.')
        symbol = _metadata_value(scanner.get('selected_symbol') or report.get('symbol') or '해당 종목')
        delta = _num_opt(scanner.get('selected_bias_adjustment'))
        if delta is not None:
            if abs(delta) < 1e-12:
                lines.append(f'- 이번 거래 후보 {symbol}에는 메모리 기반 추가 가감점이 없었습니다.')
            else:
                lines.append(f'- 이번 거래 후보 {symbol}에는 메모리 기반 가감점 {delta:+0.3f}이 반영됐습니다.')
        reason = ', '.join((str(x) for x in _listify(scanner.get('reason')) if str(x).strip()))
        if reason:
            summary = _reason_summary_line(_listify(scanner.get('reason')), '스캐너 조정은')
            if summary:
                lines.append(summary)
    else:
        lines.append('- 스캐너 메모리 가중치의 실제 delta는 이 거래 artifact에 기록되지 않았습니다.')
    if monitor.get('captured'):
        active_layers_text = _memory_layers_text(monitor.get('active_layers'))
        state = '진입 정책에 적용된 상태' if monitor.get('applied') else '요약만 기록된 상태'
        lines.append(f'- 모니터 메모리 조정은 {state}이며, 실제 반영 레이어는 {active_layers_text}입니다.')
        active_layers = [str(x) for x in _listify(monitor.get('active_layers')) if str(x).strip()]
        if monitor.get('applied') and active_layers:
            lines.append(f'- 이번 거래에서는 모니터가 {_memory_layers_text(active_layers)} 메모리를 진입 판단에 직접 반영했습니다.')
        deltas = []
        for row in _listify(monitor.get('applied_deltas')):
            row = _as_dict(row)
            if not row:
                continue
            deltas.append(f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})")
        if deltas:
            lines.append(f"- 진입 정책 변화는 {', '.join(deltas)}입니다.")
            interpretation = _monitor_delta_interpretation(_listify(monitor.get('applied_deltas')))
            if interpretation:
                lines.append(f'- 진입 적용 해석: {interpretation}')
        else:
            lines.append('- 모니터 진입 정책 변화는 이 거래 artifact에 기록되지 않았습니다.')
        hold_deltas = []
        for row in _listify(monitor.get('hold_deltas')):
            row = _as_dict(row)
            if not row:
                continue
            hold_deltas.append(f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})")
        if hold_deltas:
            lines.append(f"- 보유 관리 변화는 {', '.join(hold_deltas)}입니다.")
            lines.append('- 보유 관리 해석: 경고 후 재확인 조건을 줄여, 보유 포지션을 더 빨리 정리할 수 있게 했습니다.')
        exit_deltas = []
        for row in _listify(monitor.get('exit_deltas')):
            row = _as_dict(row)
            if not row:
                continue
            exit_deltas.append(f"{row.get('field')} {float(row.get('from')):0.3f} -> {float(row.get('to')):0.3f} ({float(row.get('delta')):+0.3f})")
        if exit_deltas:
            lines.append(f"- 청산 정책 변화는 {', '.join(exit_deltas)}입니다.")
            lines.append('- 청산 정책 해석: 손실과 drawdown 기준을 더 타이트하게 잡아, 손상이 확인되면 더 빨리 청산하도록 조정했습니다.')
        lines.append(f"- 모니터 위험 자세는 {_playbook_label(monitor.get('risk_posture') or '-')}이었고, 최종 정책 기준은 {_policy_source_label(monitor.get('effective_policy_source') or '-')}이었습니다.")
        reason = ', '.join((str(x) for x in _listify(monitor.get('reason')) if str(x).strip()))
        if reason:
            summary = _reason_summary_line(_listify(monitor.get('reason')), '모니터 조정은')
            if summary:
                lines.append(summary)
    else:
        lines.append('- 모니터 메모리 조정의 실제 delta는 이 거래 artifact에 기록되지 않았습니다.')
    return lines
