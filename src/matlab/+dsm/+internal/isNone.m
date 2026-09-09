function tf = isNone(value)
%isNone True for the reader's "no value" marker ([]), false for any real value including ""
    tf = isnumeric(value) && isempty(value);
end
