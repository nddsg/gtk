"use strict";

var debug = true;
var long_delay = 2000;
var short_delay = 400;

function surveyQuestionClosure(text, globalState, result_variable, delay, callback) {
    if (debug) console.log("Survey question closure was called.");

	var question = $("#question");
	var buttonLeft = $("#button-left");
	var buttonRight = $("#button-right");
	
	return function() {
		if (debug) console.log("Survey question function was called.");
		buttonLeft.fadeIn();
		buttonRight.fadeIn();
		question.promise().done(function(){$(this).text(text).fadeIn();});
		buttonLeft.unbind("click").click(function(){
    		question.fadeOut(delay);
			buttonLeft.fadeOut(delay);
			buttonRight.fadeOut(delay);
			result_variable = globalState.surveyQuestionData.image1.image_id;
			if (callback !== undefined) callback();
		});
		buttonRight.unbind("click").click(function(){
    		question.fadeOut(delay);
    		buttonLeft.fadeOut(delay);
			buttonRight.fadeOut(delay);
			result_variable = globalState.surveyQuestionData.image2.image_id;
			if (callback !== undefined) callback();
		});
	}
}

function loadPair(globalState, callback, delayOut=long_delay, delayIn=short_delay) {
    
    if (debug) console.log("loadPair was called.");
    
    $("#left-image").fadeOut(delayOut);        
    $("#right-image").fadeOut(delayOut);
    $("#caption-subreddit").fadeOut(delayOut);
    $("#caption-left").fadeOut(delayOut);
    $("#caption-right").fadeOut(delayOut);
    $("#result-left").fadeOut(delayOut);
    $("#result-right").fadeOut(delayOut);

    
    var postData = {};
    
    // Check if roundData is non-null; if it is valid, include it in the request for the server to record
    if (globalState.roundData.preferredChoice !== null &&
        globalState.roundData.upvoteChoice !== null &&
        globalState.roundData.preferredChoiceTime !== null &&
        globalState.roundData.upvoteChoiceTime !== null
       ) {
           postData = globalState.roundData;
       }
    
    
    // Send the request as a POST request. If there is not valid data, nothing will be sent. If there is valid data, it will be sent. The request will be a new pair of images, regardless.
    $.post("/random_pair.json", postData, function(data) {
        if (debug) console.log("In loadPair: data was returned from the server.");
        
        globalState.startTime = new Date();
        globalState.surveyQuestionData = data;
        globalState.roundNumber++;
        
        var leftImage = $("#left-image").promise();
        var rightImage = $("#right-image").promise();
        var captionSubreddit = $("#caption-subreddit").promise();
        var captionLeft = $("#caption-left").promise();
        var captionRight = $("#caption-right").promise();
        
        // Modify the respective HTML elements by inserting the new data
        leftImage.done(function(){
            $(this).attr("src", data.image1.url).attr("alt", data.image1.title).fadeIn(delayIn);        
        });
            
        rightImage.done(function(){
            $(this).attr("src", data.image2.url).attr("alt", data.image2.title).fadeIn(delayIn);
        });
        captionSubreddit.done(function(){
            $(this).text(data.image1.subreddit).fadeIn(delayIn);
        });
        captionLeft.done(function(){
            $(this).text(data.image1.title).fadeIn(delayIn);
        });
        captionRight.done(function(){
            $(this).text(data.image2.title).fadeIn(delayIn);
        });
        $("#result-left").promise().done(function(){
            $(this).text("Upvotes: " + data.image1.score);
        });
        $("#result-right").promise().done(function(){
            $(this).text("Upvotes: " + data.image2.score);
        });
            
        if (callback !== undefined) {    
            $.when.apply(null, [leftImage, rightImage, captionSubreddit, captionLeft, captionRight]).done(function(){
                callback();  
            });
        }
        
    }, 'json');
}

$(document).ready(function (){
    
    var roundData = {
        preferredChoiceTime: null,
        upvoteChoiceTime: null,
        preferredChoice: null,
        upvoteChoice: null
    };
    
    var globalState = {
        startTime: null,
        surveyQuestionData: null,
        roundNumber: 0,
        roundData: roundData
    };
        
    // Declare all survey questions here; define what they are later. Necessary because of interdependencies.
    var upvoteQuestion, preferQuestion;
    
    
    upvoteQuestion = surveyQuestionClosure(
        "Which got more upvotes?",
        globalState,
        globalState.roundData.upvoteChoice,
        0,
        function () {
            // Calculate the time delta it took the user to press the button
            var currentTime = new Date();
            roundData.upvoteChoiceTime = currentTime - globalState.startTime;
            
            $("#result-left").fadeIn(short_delay);
            $("#result-right").fadeIn(short_delay);
            
            // Load the next pair of images...
            loadPair(globalState, preferQuestion);
        }
    );

	preferQuestion = surveyQuestionClosure(
	    "Which do you prefer?",
	    globalState,
	    globalState.roundData.preferredChoice,
	    short_delay,
	    function() {
        	// Calculate the time delta it took the user to press the button
        	var currentTime = new Date();
        	roundData.preferredChoiceTime = currentTime - globalState.startTime;
        	
        	// Reset the time for the next question
        	globalState.startTime = currentTime;
        	
        	// Display the next survey question
        	upvoteQuestion()
        }
    );
    
    
    // Load the first set of questions
    loadPair(globalState, preferQuestion, 0, 0);
    
    // Get the list of subreddits to populate the dropdown menu
    $.getJSON("/dropdown_populate.json", function(data) {
        if (debug) console.log(data);
        var option = $("#dropdown-populate");
        $.each(data.subreddit, function(_, i){
            option.append(
                $("<li>", {role: "presentation"}).append(
                    $("<a>", {role: "menuitem", href:"#"}).text(i)
                )
            );
        })
    })
})