function text = applySlice(text, spec)
%applySlice A Python-style slice "start:stop" of a string: 0-based, half-open, negative from the end
    arguments
        text (1,1) string
        spec (1,1) string
    end
    bounds = split(spec, ":");
    n = strlength(text);
    start = resolveBound(bounds(1), 0, n);
    stop = resolveBound(bounds(2), n, n);
    if stop <= start
        text = "";
    else
        text = extractBetween(text, start + 1, stop);
    end
end

function index = resolveBound(bound, default, n)
    if bound == ""
        index = default;
        return
    end
    index = str2double(bound);
    if index < 0
        index = max(n + index, 0);
    else
        index = min(index, n);
    end
end
