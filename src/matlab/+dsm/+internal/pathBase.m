function name = pathBase(entry)
%pathBase The last component of an entry, without a trailing '/'
    parts = split(regexprep(string(entry), "/$", ""), "/");
    name = parts(end);
end
