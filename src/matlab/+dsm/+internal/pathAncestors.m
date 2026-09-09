function parents = pathAncestors(entry)
%pathAncestors Every ancestor directory of an entry, outermost first, each ending with '/'
    parts = split(regexprep(string(entry), "/$", ""), "/");
    parents = string.empty(1, 0);
    for i = 1:numel(parts) - 1
        parents(end+1) = join(parts(1:i), "/") + "/"; %#ok<AGROW>
    end
end
