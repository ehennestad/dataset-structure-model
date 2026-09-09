classdef Listing
%Listing A directory snapshot under one or more root storage paths (DirectoryListing.schema.json)
%
%   Roots is a row cell array of structs with fields DataLocation,
%   RootStoragePath and Entries (a row cell array of char, sorted, with
%   every ancestor directory present and directories ending in '/').

    properties
        Roots (1,:) cell = {}
        Environment (1,1) string = ""
    end

    methods
        function obj = Listing(roots, environment)
            arguments
                roots (1,:) cell = {}
                environment (1,1) string = ""
            end
            obj.Roots = roots;
            obj.Environment = environment;
        end

        function doc = toStruct(obj)
            roots = cell(1, numel(obj.Roots));
            for i = 1:numel(obj.Roots)
                roots{i} = struct( ...
                    "dataLocationIdentifier", obj.Roots{i}.DataLocation, ...
                    "rootStoragePathIdentifier", obj.Roots{i}.RootStoragePath, ...
                    "entries", {obj.Roots{i}.Entries});
            end
            doc = struct("roots", {roots});
            if obj.Environment ~= ""
                doc = struct("environmentIdentifier", obj.Environment, "roots", {roots});
            end
        end

        function text = toJson(obj)
            text = string(jsonencode(obj.toStruct(), "PrettyPrint", true)) + newline;
        end

        function write(obj, path)
            arguments
                obj
                path (1,1) string
            end
            fid = fopen(path, "w");
            cleanup = onCleanup(@() fclose(fid));
            fwrite(fid, obj.toJson(), "char");
        end
    end

    methods (Static)
        function root = makeRoot(dataLocation, rootStoragePath, entries)
            arguments
                dataLocation (1,1) string
                rootStoragePath (1,1) string
                entries (1,:) cell
            end
            root = struct("DataLocation", dataLocation, "RootStoragePath", rootStoragePath, ...
                "Entries", {dsm.internal.normalizeEntries(entries)});
        end

        function obj = fromStruct(doc)
        %fromStruct Build a Listing from a decoded listing document, validating it first
            errors = dsm.schemaErrors(doc, "DirectoryListing.schema.json");
            if ~isempty(errors)
                error("dsm:listing:Invalid", "Invalid listing:\n%s", strjoin(errors, newline))
            end
            items = dsm.internal.asCellOfStructs(doc.roots);
            roots = cell(1, numel(items));
            for i = 1:numel(items)
                roots{i} = dsm.Listing.makeRoot(items{i}.dataLocationIdentifier, ...
                    items{i}.rootStoragePathIdentifier, dsm.internal.asCellstr(items{i}.entries));
            end
            obj = dsm.Listing(roots, string(dsm.internal.getField(doc, "environmentIdentifier", "")));
        end

        function obj = fromFile(path)
            obj = dsm.Listing.fromStruct(dsm.internal.readJson(path));
        end
    end
end
