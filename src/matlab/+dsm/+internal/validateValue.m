function problem = validateValue(value, definition)
%validateValue A problem description when the value violates the definition's validation, else ""
    problem = "";
    rules = dsm.internal.getField(definition, "validation", []);
    if isempty(rules)
        return
    end
    if isfield(rules, "enum")
        allowed = rules.enum;
        if iscell(allowed)
            ok = any(cellfun(@(a) isequal(string(a), string(value)) || isequal(a, value), allowed));
        else
            ok = any(allowed == value);
        end
        if ~ok
            problem = sprintf("%s is not one of the allowed values", string(value));
            return
        end
    end
    if ischar(value) || isstring(value)
        text = char(value);
        if isfield(rules, "pattern") && isempty(regexp(text, rules.pattern, "once"))
            problem = sprintf("'%s' does not match %s", text, rules.pattern);
        elseif isfield(rules, "minLength") && strlength(text) < rules.minLength
            problem = sprintf("'%s' is shorter than %d", text, rules.minLength);
        elseif isfield(rules, "maxLength") && strlength(text) > rules.maxLength
            problem = sprintf("'%s' is longer than %d", text, rules.maxLength);
        end
    elseif isnumeric(value) && ~islogical(value)
        if isfield(rules, "minimum") && value < rules.minimum
            problem = sprintf("%g is below %g", value, rules.minimum);
        elseif isfield(rules, "maximum") && value > rules.maximum
            problem = sprintf("%g is above %g", value, rules.maximum);
        end
    end
end
