function value = normalizeValue(value, rule)
%normalizeValue Apply an extraction rule's normalize step to a text value
    mode = string(dsm.internal.getField(rule, "normalize", "none"));
    argument = string(dsm.internal.getField(rule, "normalizePattern", ""));
    value = string(value);
    switch mode
        case "lowercase"
            value = lower(value);
        case "uppercase"
            value = upper(value);
        case "trim"
            value = strtrim(value);
        case "strip_prefix"
            if argument ~= "" && startsWith(value, argument)
                value = extractAfter(value, strlength(argument));
            end
        case "strip_suffix"
            if argument ~= "" && endsWith(value, argument)
                value = extractBefore(value, strlength(value) - strlength(argument) + 1);
            end
        otherwise
            % "none": leave the value as extracted
    end
end
