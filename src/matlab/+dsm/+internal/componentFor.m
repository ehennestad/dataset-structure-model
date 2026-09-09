function component = componentFor(rule, levelNames, relPath)
%componentFor The path component a rule reads: a level's component, or the whole relative path
%   Returns [] when the referenced level lies beyond the path.
    levelRef = dsm.internal.getField(rule, "entityLayoutLevel", []);
    stripped = regexprep(char(relPath), "/$", "");
    if isempty(levelRef)
        component = string(stripped);
        return
    end
    parts = split(string(stripped), "/");
    if isnumeric(levelRef)
        index = levelRef + 1;  % the schema's level indices are 0-based
    else
        index = find(levelNames == string(levelRef), 1);
    end
    if index <= numel(parts)
        component = parts(index);
    else
        component = [];
    end
end
