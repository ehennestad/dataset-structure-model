classdef Tree
%Tree Children lookup over one root's listing entries

    properties (SetAccess = immutable)
        Entries (1,:) cell
    end

    properties (Access = private)
        Children containers.Map
    end

    methods
        function obj = Tree(entries)
            arguments
                entries (1,:) cell
            end
            obj.Entries = sort(entries);
            obj.Children = containers.Map("KeyType", "char", "ValueType", "any");
            for entry = obj.Entries
                parent = char(dsm.internal.pathParent(entry{1}));
                if isKey(obj.Children, parent)
                    obj.Children(parent) = [obj.Children(parent), entry];
                else
                    obj.Children(parent) = entry;
                end
            end
        end

        function entries = children(obj, directory)
        %children Direct children of a directory entry ("" for the root), sorted
            key = char(directory);
            if isKey(obj.Children, key)
                entries = obj.Children(key);
            else
                entries = {};
            end
        end

        function files = childFiles(obj, directory)
            entries = obj.children(directory);
            files = entries(~cellfun(@dsm.internal.isDirEntry, entries));
        end
    end
end
