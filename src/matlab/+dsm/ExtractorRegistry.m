classdef ExtractorRegistry < handle
%ExtractorRegistry Implementations of `function` extraction rules, keyed by extractorFunction
%
%   An implementation is a function handle called as
%       value = fcn(fullPath, levelName, dataLocationIdentifier)
%   returning a value of the field's dataType, or [] when it cannot extract.

    properties (Access = private)
        Functions containers.Map
    end

    methods
        function obj = ExtractorRegistry(functions)
            arguments
                functions (1,1) struct = struct()
            end
            obj.Functions = containers.Map("KeyType", "char", "ValueType", "any");
            for key = string(fieldnames(functions))'
                obj.Functions(char(key)) = functions.(key);
            end
        end

        function register(obj, key, fcn)
            arguments
                obj
                key (1,1) string
                fcn (1,1) function_handle
            end
            obj.Functions(char(key)) = fcn;
        end

        function fcn = get(obj, key)
            if isKey(obj.Functions, char(key))
                fcn = obj.Functions(char(key));
            else
                fcn = [];
            end
        end

        function tf = has(obj, key)
            tf = isKey(obj.Functions, char(key));
        end

        function names = keys(obj)
            names = sort(string(keys(obj.Functions)));
            names = reshape(names, 1, []);
        end
    end
end
