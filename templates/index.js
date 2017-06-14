"use strict";

function surveyQuestionClosure(text, callback) {
	return function() {
		$("#question").text(text);
		$("#button-left").click(function(){
			this.buttonClicked = "left";
			if (callback !== undefined) callback();
		});
		$("#button-right").click(function(){
			this.buttonClicked = "right";
			if (callback !== undefined) callback();
		});
	}
}

$(document).ready(function (){

    $.getJSON("/random_pair.json", function(data) {
        console.log(data);
        $("#left-image").attr("src", data.image1.url).attr("alt", data.image1.title);
        $("#right-image").attr("src", data.image2.url).attr("alt", data.image2.title);
        $("#caption-subreddit").text(data.image1.subreddit);
        $("#caption-left").text(data.image1.title);
        $("#caption-right").text(data.image2.title);
        
    })
    
    $.getJSON("/dropdown_populate.json", function(data) {
        console.log(data);
        var option = $("#dropdown-populate");
        $.each(data.subreddit, function(_, i){
            option.append(
                $("<li>", {role: "presentation"}).append(
                    $("<a>", {role: "menuitem", href:"#"}).text(i)
                )
            );
        })
    })

	var upvoteQuestion = surveyQuestionClosure("Which got more upvotes?", function(){alert("done");});

	var preferQuestion = surveyQuestionClosure("Which do you prefer?", upvoteQuestion);

	preferQuestion();

})