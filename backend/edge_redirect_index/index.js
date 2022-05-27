exports.handler = function (event, context, callback) {
    const request = event.Records[0].cf.request;
    const uri = request.uri;
    // Check whether the URI is missing a file name.
    if (uri.endsWith('/')) {
        request.uri += 'index.html';
        console.log("URI rewrote from: "+uri+" to: "+ request.uri);
    }
    // Check whether the URI is missing a file extension.
    else if (!uri.includes('.')) {
        console.log("Redirecting from:"+uri+"to "+uri+"/");
        let locationUrl =  `https://${request.headers.host[0].value}${uri}/`
        if (request.querystring) {
            locationUrl += `?${request.querystring}`
        }
        return callback(null,  {
            status: '302',
            headers: {
                'location': [{
                    key: 'location',
                    value: locationUrl
                }]
            }
        });
    }

    return callback(null, request);
}