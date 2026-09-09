function errors = schemaErrors(doc, schemaName)
%schemaErrors Validate a decoded document against one of the DSM schemas
%
%   errors = dsm.schemaErrors(doc) validates a config against
%   DatasetStructureModel.schema.json and returns a string array of
%   problems, empty when valid.
%
%   errors = dsm.schemaErrors(doc, schemaName) validates against another
%   schema in the repository's schema folder (EntityRecord.schema.json,
%   DirectoryListing.schema.json).

    arguments
        doc
        schemaName (1,1) string = "DatasetStructureModel.schema.json"
    end
    errors = dsm.internal.schemaValidationErrors(doc, dsm.internal.loadSchema(schemaName));
end
