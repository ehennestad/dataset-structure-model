function tf = isDirEntry(entry)
%isDirEntry True for a listing entry that denotes a directory (ends with '/')
    tf = endsWith(string(entry), "/");
end
