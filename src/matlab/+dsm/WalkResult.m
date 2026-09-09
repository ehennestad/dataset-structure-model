classdef WalkResult
%WalkResult What a walk produces: entity records, unmatched entries, and context
%
%   Records is a row cell array of structs in the EntityRecord shape:
%   entityType, identity (struct), parents (cell of structs), locations
%   (cell of structs; files is a containers.Map), metadata (struct), issues
%   (cell of structs). Unmatched is a row cell array of structs with
%   dataLocationIdentifier, rootStoragePathIdentifier, path, reason, detail.

    properties
        Records (1,:) cell = {}
        Unmatched (1,:) cell = {}
        Environment (1,1) string = ""
        Roots (1,:) cell = {}
        UnresolvedExtractors (1,:) string = string.empty(1, 0)
        Warnings (1,:) string = string.empty(1, 0)
    end

    methods
        function doc = toStruct(obj, options)
        %toStruct The {records, unmatched} document in the schema's JSON shape
            arguments
                obj
                options.IncludeDetail (1,1) logical = true
            end
            unmatched = obj.Unmatched;
            if ~options.IncludeDetail
                for i = 1:numel(unmatched)
                    unmatched{i} = rmfield(unmatched{i}, "detail");
                end
            end
            doc = struct("records", {obj.Records}, "unmatched", {unmatched});
        end

        function text = toJson(obj, options)
            arguments
                obj
                options.IncludeDetail (1,1) logical = true
            end
            text = string(jsonencode(obj.toStruct("IncludeDetail", options.IncludeDetail), "PrettyPrint", true)) + newline;
        end

        function write(obj, path, options)
            arguments
                obj
                path (1,1) string
                options.IncludeDetail (1,1) logical = true
            end
            fid = fopen(path, "w");
            cleanup = onCleanup(@() fclose(fid));
            fwrite(fid, obj.toJson("IncludeDetail", options.IncludeDetail), "char");
        end
    end
end
