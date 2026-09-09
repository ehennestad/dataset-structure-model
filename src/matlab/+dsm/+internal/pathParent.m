function parent = pathParent(entry)
%pathParent The directory an entry sits in ("" for the root), ending with '/'
    parts = split(regexprep(string(entry), "/$", ""), "/");
    if numel(parts) <= 1
        parent = "";
    else
        parent = join(parts(1:end-1), "/") + "/";
    end
end
