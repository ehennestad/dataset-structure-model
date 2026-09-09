function listing = loadListing(path)
%loadListing Load a listing.json into a dsm.Listing
    arguments
        path (1,1) string
    end
    listing = dsm.Listing.fromFile(path);
end
