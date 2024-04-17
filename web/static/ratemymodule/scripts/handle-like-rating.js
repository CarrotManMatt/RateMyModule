document.addEventListener("DOMContentLoaded", function() {

    // Getting all the posts the current user has liked and disliked
    fetch('/like-dislike-post/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if ((data.liked_posts) && (data.disliked_posts)) {
            likedPosts = data.liked_posts;
            dislikedPosts = data.disliked_posts;

        } else {
            console.log("Error: " + data.error);
        }

        var RatingArrows = document.querySelectorAll('.post-like-rating-arrow');
        // console.log("RatingArrows: " + RatingArrows.length);

        var likeArrows = document.querySelectorAll('.like-rating-up-arrow');
        var dislikeArrows = document.querySelectorAll('.like-rating-down-arrow');
        // console.log("likeArrows: " + likeArrows.length);
        // console.log("dislikeArrows: " + dislikeArrows.length);

        RatingArrows.forEach(function(arrow) {
            var index = -1;
            var postPK = arrow.dataset.postPK;

            // Find index of current arrow
            for (var i = 0; i < RatingArrows.length; i++) {
                if (RatingArrows[i] === arrow) {
                    index = i;
                    break;
                }
            }

            // Toggling currently liked/disliked arrows on page load
            if (likedPosts.indexOf(Number(postPK)) !== -1){
                likeArrows[Math.floor(index / 2)].classList.add('post-like-rating-arrow-clicked');
            } else if (dislikedPosts.indexOf(Number(postPK)) !== -1) {
                dislikeArrows[Math.floor(index/2)].classList.add('post-like-rating-arrow-clicked');
            }

            // Handle 'onClick' for rating arrows
            arrow.addEventListener('click', function() {
                console.log("Current Arrow Index: " + index);

                var likeDislikeIndex = Math.floor(index / 2);
                console.log("Current post number: " + likeDislikeIndex);

                if (arrow.classList.contains('like-rating-up-arrow')) {
                    // Handling Like Arrow Clicked
                    console.log("Current Arrow Type: Like");
                    if (dislikeArrows[likeDislikeIndex].classList.contains('post-like-rating-arrow-clicked')) {
                        dislikeArrows[likeDislikeIndex].classList.remove('post-like-rating-arrow-clicked');
                    }
                    likeArrows[likeDislikeIndex].classList.toggle('post-like-rating-arrow-clicked');
                    ratePost(postPK, "like");

                } else if (arrow.classList.contains('like-rating-down-arrow')) {
                    // Handling Dislike Arrow Clicked
                    console.log("Current Arrow Type: Dislike");
                    if (likeArrows[likeDislikeIndex].classList.contains('post-like-rating-arrow-clicked')) {
                        likeArrows[likeDislikeIndex].classList.remove('post-like-rating-arrow-clicked');
                    }
                    dislikeArrows[likeDislikeIndex].classList.toggle('post-like-rating-arrow-clicked');
                    ratePost(postPK, "dislike");
                }
            });
        });

    });
});

function ratePost(postPK, action) {
    var csrftoken = getCookie('csrftoken');

    fetch('/like-dislike-post/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: 'post_pk=' + postPK + `&action=${action}`
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.error) {
            // Display error message to the user
            alert('Error: ' + data.error);
        } else {
            // Handle successful response
            console.log(`${action}: ` + data.message);
        }
    })
    .catch(function(error) {
        console.error('Error sending POST request:', error);
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
