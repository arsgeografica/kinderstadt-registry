from itertools import chain


def parse_range(rng):
    parts = rng.split('-')
    if 1 > len(parts) > 2:
        raise ValueError('Bad range: "%s"' % rng)
    try:
        parts = [int(i) for i in parts]
    except ValueError:
        return []
    start = parts[0]
    end = start if len(parts) == 1 else parts[1]
    if start > end:
        end, start = start, end
    return range(start, end + 1)


def pass_spec_parser(spec):
    if not spec:
        return []
    return sorted(set(chain(*[parse_range(rng) for rng in spec.split(',')])))


def pass_spec_builder(ids):
    spec = []
    for id in sorted(ids):
        if 0 == len(spec) or spec[-1][-1] != id - 1:
            spec.append([id])
        else:
            spec[-1].append(id)

    return ','.join(['%d-%d' % (r[0], r[-1]) if r[0] != r[-1] else '%d' % r[0]
                    for r in spec])
