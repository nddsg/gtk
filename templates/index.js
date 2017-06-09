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
        $("#left-image").attr("src", data.image1);
        $("#right-image").attr("src", data.image2);
    })

	var upvoteQuestion = surveyQuestionClosure("Which got more upvotes?", function(){alert("done");});

	var preferQuestion = surveyQuestionClosure("Which do you prefer?", upvoteQuestion);

	preferQuestion();

})