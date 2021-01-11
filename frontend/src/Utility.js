export function createGetRequestUrl(baseUrl, path, queryParameters) {
    let url = new URL(baseUrl);
    url.pathname = path;
    url.search = new URLSearchParams(queryParameters).toString();
    return url;
}