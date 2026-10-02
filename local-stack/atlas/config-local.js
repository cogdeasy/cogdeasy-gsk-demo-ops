define([], function () {
	var configLocal = {};

	// ATLAS and WebAPI are served from the same origin by the proxy service.
	var baseUrl = window.location.protocol + "//" + window.location.host;

	configLocal.api = {
		name: "GSK Cohort Analytics (local)",
		url: baseUrl + "/WebAPI/"
	};

	configLocal.cohortComparisonResultsEnabled = false;
	configLocal.userAuthenticationEnabled = false;
	configLocal.plpResultsEnabled = false;
	configLocal.disableBrowserCheck = true;
	configLocal.enableTermsAndConditions = false;
	configLocal.enablePersonCount = true;
	configLocal.cacheSources = false;
	configLocal.pollInterval = 60000;

	return configLocal;
});
