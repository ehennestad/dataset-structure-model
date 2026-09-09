classdef ConfigError < MException
%ConfigError A config a reader must refuse; Code is a conformance error code
%
%   Codes: "schema-validation", "reference-integrity", "unsupported-draft".
%   The MException identifier is dsm:config:<code in camelCase>.

    properties (SetAccess = immutable)
        Code (1,1) string
        Problems (1,:) string
    end

    methods
        function obj = ConfigError(code, problems)
            arguments
                code (1,1) string
                problems (1,:) string
            end
            mnemonic = regexprep(code, "-(\w)", "${upper($1)}");
            obj@MException("dsm:config:" + mnemonic, "%s: %s", code, strjoin(problems, "; "));
            obj.Code = code;
            obj.Problems = problems;
        end
    end
end
