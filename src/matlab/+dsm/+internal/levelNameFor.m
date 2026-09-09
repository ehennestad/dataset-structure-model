function name = levelNameFor(rule, levelNames)
%levelNameFor The level name a rule reads from, or "" for the whole path
    levelRef = dsm.internal.getField(rule, "entityLayoutLevel", []);
    if isempty(levelRef)
        name = "";
    elseif isnumeric(levelRef)
        name = levelNames(levelRef + 1);
    else
        name = string(levelRef);
    end
end
