from flask import current_app, jsonify, render_template, request
from registry.models import Visit


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


def chart():
    bins = {}
    start_time = current_app.config['START_TIME']
    end_time = current_app.config['END_TIME']
    max_in = 0
    max_out = 0
    for _bin in Visit.binned(300):
        ts_d = _bin.ts.date()
        ts_t = _bin.ts.time()

        ts_t = start_time if ts_t < start_time else ts_t
        ts_t = end_time if ts_t > end_time else ts_t

        ts_d = ts_d.isoformat()
        ts_t = ts_t.isoformat()

        if ts_d not in bins:
            bins[ts_d] = {}
        if ts_t not in bins[ts_d]:
            bins[ts_d][ts_t] = {}
        mode = 'check_in' if _bin.is_check_in else 'check_out'
        if 'check_in' == mode:
            max_in = max(max_in, _bin.count)
        else:
            max_out = max(max_out, _bin.count)
        bins[ts_d][ts_t][mode] = _bin.count

    if request_wants_json():
        return jsonify(data=bins)

    return render_template('chart/chart.html',
                           bins=bins,
                           start_time=start_time,
                           end_time=end_time,
                           max_in=max_in,
                           max_out=max_out)
