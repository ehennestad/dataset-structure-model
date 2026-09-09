function result = walk(config, listing, registry)
%walk Walk a directory listing into entity records
%
%   result = dsm.walk(config, listing) returns a dsm.WalkResult whose
%   Records follow schema/EntityRecord.schema.json. Pass a
%   dsm.ExtractorRegistry to implement `function` extraction rules.

    arguments
        config (1,1) dsm.Config
        listing (1,1) dsm.Listing
        registry (1,1) dsm.ExtractorRegistry = dsm.ExtractorRegistry()
    end
    walker = dsm.internal.Walker(config, registry);
    result = walker.walk(listing);
end
