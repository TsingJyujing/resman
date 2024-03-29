import $ from 'jquery';

export function createGetRequestUrl(path, queryParameters) {
    let url = new URL(window.location);
    url.pathname = path;
    url.search = new URLSearchParams(queryParameters).toString();
    return url;
}

export function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


export function postData(url, data) {
    return fetch(
        url,
        {
            method: 'POST',
            body: JSON.stringify(data), // must match 'Content-Type' header
            cache: 'no-cache',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
            },
            redirect: 'follow', // manual, *follow, error
        }
    )
}


export function postForm(url, formData) {
    return fetch(
        url,
        {
            method: 'POST',
            body: formData,
            cache: 'no-cache',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json"
            },
        }
    )
}


/**
 * Handle reaction operations, return event function on click like/dislike button
 * @param currentReaction variable of current reaction status
 * @param apiUrl should be /api/{item}/{id}/reaction
 * @param onSuccess a function after reaction was set successfully, like burst the cache
 * @param onError will be called while error
 * @returns {{clickDislike: clickDislike, clickLike: clickLike}}
 */
export function createReactionOperations(
    currentReaction,
    apiUrl,
    onSuccess,
    onError = (response) => {
        console.error(response)
    }
) {
    return {
        clickLike: () => {
            postData(
                apiUrl,
                {positive_reaction: (currentReaction === true ? null : true)}
            ).then(response => {
                if (response.ok) {
                    onSuccess(response);
                } else {
                    onError(response);
                }
            });
        },
        clickDislike: () => {
            postData(
                apiUrl,
                {positive_reaction: (currentReaction === false ? null : false)}
            ).then(response => {
                if (response.ok) {
                    onSuccess(response);
                } else {
                    onError(response);
                }
            });
        }
    };
}

/**
 * close current window with confirm or not
 * @param withConfirm
 */
function closeWindow(withConfirm) {
    if (!withConfirm || confirm("Close the window?")) {
        window.opener = null;
        window.open('', '_self');
        window.close();
    }
}

export function deleteContent(url) {
    if (confirm("Are you sure to delete?")) {
        return fetch(
            url,
            {
                method: 'DELETE',
                cache: 'no-cache',
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken")
                },
                redirect: 'follow',
            }
        ).then(response => {
            console.log(`${url} deleted successfully`);
            console.log(response);
            if (response.ok) {
                alert("Deleted successfully")
                closeWindow(false)
            } else {
                alert("Deleted failed.")
            }
        })
    }
}

/**
 *
 * @param a1
 * @param a2
 */
export function arrayEquals(a1, a2) {
    try {
        if (a1.length != a2.length) {
            return false;
        }
        for (let i = 0, l = a1.length; i < l; i++) {
            if (a1[i] != a2[i]) {
                return false;
            }
        }
        return true;
    } catch (e) {
        return false;
    }
}

export function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
