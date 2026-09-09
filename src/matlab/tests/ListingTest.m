classdef ListingTest < matlab.unittest.TestCase
%ListingTest Listing construction from JSON, directories and find-style text

    methods (Test)
        function findOutputInfersDirectories(testCase)
            root = dsm.listing.fromLines("raw", "main", ["./m110/20250523_baseline/movie.tif", "m110/notes.txt", "", "# comment", "empty/"]);
            testCase.verifyEqual(root.Entries, {'empty/', 'm110/', 'm110/20250523_baseline/', 'm110/20250523_baseline/movie.tif', 'm110/notes.txt'});
        end

        function listingAddsMissingAncestorsAndRejectsBadPaths(testCase)
            doc = struct("roots", struct("dataLocationIdentifier", "raw", "rootStoragePathIdentifier", "main", "entries", {{'a/b/c.txt'}}));
            listing = dsm.Listing.fromStruct(doc);
            testCase.verifyEqual(listing.Roots{1}.Entries, {'a/', 'a/b/', 'a/b/c.txt'});
            bad = struct("roots", struct("dataLocationIdentifier", "raw", "rootStoragePathIdentifier", "main", "entries", {{'../x'}}));
            testCase.verifyError(@() dsm.Listing.fromStruct(bad), "dsm:listing:Invalid");
        end

        function walkRealDirectory(testCase)
            folder = testCase.applyFixture(matlab.unittest.fixtures.TemporaryFolderFixture).Folder;
            mkdir(fullfile(folder, "m110", "20250523_baseline"));
            fclose(fopen(fullfile(folder, "m110", "20250523_baseline", "movie.tif"), "w"));
            mkdir(fullfile(folder, "temp"));
            root = dsm.listing.fromDirectory("raw", "main", folder);
            testCase.verifyEqual(root.Entries, {'m110/', 'm110/20250523_baseline/', 'm110/20250523_baseline/movie.tif', 'temp/'});
            result = dsm.walk(dsm.Config(minimalConfigDoc()), dsm.Listing({root}));
            testCase.verifyEqual(cellfun(@(r) r.entityType, result.Records), ["subject", "session"]);
            testCase.verifyEqual(result.Records{2}.metadata, struct("subject_id", "m110", "session_id", "baseline"));
            testCase.verifyEqual(cellfun(@(u) u.path, result.Unmatched), "temp/");
        end

        function listingRoundTripsThroughJson(testCase)
            listing = dsm.Listing({dsm.Listing.makeRoot("raw", "main", {'a/b.txt'})}, "lab");
            decoded = jsondecode(listing.toJson());
            testCase.verifyEqual(decoded.environmentIdentifier, 'lab');
            testCase.verifyEqual(decoded.roots.entries, {'a/'; 'a/b.txt'});
        end
    end
end
