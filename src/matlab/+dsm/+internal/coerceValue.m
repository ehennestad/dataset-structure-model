function value = coerceValue(value, definition, rule)
%coerceValue Type a raw extracted value per the definition's dataType; [] when it cannot be typed
%
%   Dates, times and datetimes are parsed with the rule's valueFormat (LDML,
%   which datetime reads natively) and returned as ISO 8601 strings.

    dataType = string(dsm.internal.getField(definition, "dataType", "string"));
    try
        switch dataType
            case {"date", "time", "datetime"}
                format = string(dsm.internal.getField(rule, "valueFormat", ""));
                if (ischar(value) || isstring(value)) && format ~= ""
                    parsed = datetime(char(value), "InputFormat", char(format));
                    switch dataType
                        case "date"
                            parsed.Format = "yyyy-MM-dd";
                        case "time"
                            parsed.Format = "HH:mm:ss";
                        otherwise
                            parsed.Format = "yyyy-MM-dd'T'HH:mm:ss";
                    end
                    value = string(parsed);
                else
                    value = string(value);
                end
            case "integer"
                value = toNumber(value);
                if ~isempty(value) && mod(value, 1) ~= 0
                    value = [];
                end
            case "number"
                value = toNumber(value);
            case "boolean"
                if ~islogical(value)
                    value = ismember(lower(strtrim(string(value))), ["true", "1", "yes"]);
                end
            otherwise
                if ischar(value) || isstring(value)
                    value = string(value);
                end
        end
    catch
        value = [];
    end
end

function value = toNumber(value)
    if ischar(value) || isstring(value)
        value = str2double(value);
        if isnan(value)
            value = [];
        end
    elseif islogical(value)
        value = double(value);
    end
end
