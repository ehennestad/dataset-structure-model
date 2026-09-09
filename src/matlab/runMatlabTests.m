function results = runMatlabTests()
%runMatlabTests Run the MATLAB reader's test suite from anywhere
%
%   results = runMatlabTests() adds src/matlab to the path, runs every test
%   in src/matlab/tests, prints the summary and fails when any test fails.

    thisDir = fileparts(mfilename("fullpath"));
    addpath(thisDir);
    addpath(fullfile(thisDir, "tests"));
    suite = matlab.unittest.TestSuite.fromFolder(fullfile(thisDir, "tests"));
    results = run(suite);
    disp(table(results))
    assertSuccess(results)
end
