"use strict";

var debug = true;
var long_delay = 2000;
var short_delay = 400;

function demographicModal() {
    var overlay = $("<div>", {style: "position: fixed; top: 0; left: 0; z-index: 10000; background-color: rgba(0,0,0,0.5); width: 100vw; height: 100vh;"});
    
    var body = $("body")
    body.css({overflow: 'hidden'}); // Prevents background scrolling
    
    var container = $("<div>", {style: "position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); background-color: #fff; border-radius: 10px; padding: 20px"});
    container.load("/demographic_survey.html", null, function() {
        if (debug) console.log("Demographic survey loaded!")
        
        container.appendTo(overlay); // Add the HTML to the page
        
        container.find(".close").click(function(){ // Wire up the elements to the event handlers in this javascript
            overlay.remove()
            body.css({overflow: 'initial'}); // unlock the body for scrolling
        }); 
    
    });
    
    body.append(overlay);
}

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
			result_variable.value = globalState.surveyQuestionData.image1.id;
			if (callback !== undefined) callback();
		});
		buttonRight.unbind("click").click(function(){
    		question.fadeOut(delay);
    		buttonLeft.fadeOut(delay);
			buttonRight.fadeOut(delay);
			result_variable.value = globalState.surveyQuestionData.image2.id;
			if (callback !== undefined) callback();
		});
	}
}

function __loadPair(globalState, postData, callback, delayOut=long_delay, delayIn=short_delay) {
    $.post("/random_pair.json", postData, function(data) {
        if (debug) {
            console.log("In loadPair: data was returned from the server. The data was:");
            console.log(data);
        }
        
        if (globalState.roundData.round_no > data.round_no && !globalState.demographicSurveyDone) {
            // The first time round_no resets, present the demographic survey
            demographicModal();
            globalState.demographicSurveyDone = true;
        }
        
        globalState.startTime = new Date();
        globalState.surveyQuestionData = data;
        
        globalState.roundData.user_id = data.user_id;
        globalState.roundData.quiz_id = data.quiz_id;
        globalState.roundData.round_id = data.round_id;
        globalState.roundData.round_no = data.round_no;
        
        globalState.roundData.preferredChoiceTime = null;
        globalState.roundData.upvoteChoiceTime = null;
        globalState.roundData.upvoteChoice.value = null;
        globalState.roundData.preferredChoice.value = null;
        globalState.roundData.correct = null;
        
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
            $(this).text(data.subreddit + " (" + (globalState.roundData.round_no + 1) + "/" + globalState.roundTotal + ")").fadeIn(delayIn);
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
        globalState.correctImageId = (data.image1.score > data.image2.score) ? data.image1.id : data.image2.id;
            
        if (callback !== undefined) {    
            $.when.apply(null, [leftImage, rightImage, captionSubreddit, captionLeft, captionRight]).done(function(){
                $("#jtron").css({backgroundColor: "rgb(240,240,240)"});
                callback();  
            });
        }
        
    }, 'json');
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
    
    if (debug) {
        console.log("Validating data to send to server:");
        console.log(globalState.roundData);
    }
    
    // Check if roundData is non-null; if it is valid, include it in the request for the server to record
    if (globalState.roundData.preferredChoice.value !== null &&
        globalState.roundData.upvoteChoice.value !== null &&
        globalState.roundData.preferredChoiceTime !== null &&
        globalState.roundData.upvoteChoiceTime !== null
       ) {
            globalState.roundData.correct = (globalState.correctImageId == globalState.roundData.upvoteChoice.value);
           postData = globalState.roundData;
       }
    
    // Send the request as a POST request. If there is not valid data, nothing will be sent. If there is valid data, it will be sent. The request will be a new pair of images, regardless.
    __loadPair(globalState, postData, callback, long_delay, short_delay);
    }

$(document).ready(function (){
    
    var roundData = {
        user_id: null,
        quiz_id: null,
        round_id: null,
        round_no: null,
        preferredChoiceTime: null,
        upvoteChoiceTime: null,
        upvoteChoice: {
            value: null
        },
        preferredChoice: {
            value: null
        },
        correct: null
    };
    
    var globalState = {
        demographicSurveyDone: false,
        startTime: null,
        surveyQuestionData: null,
        roundNumber: 0,
        roundTotal: 10,
        roundData: roundData,
        correctImageId: null,
    };
    
    // Declare all survey questions here; define what they are later. Necessary because of interdependencies.
    var upvoteQuestion, preferQuestion;
    
    upvoteQuestion = surveyQuestionClosure(
        "Which got more upvotes?",
        globalState,
        globalState.roundData.upvoteChoice,
        0,
        function () {
            if (globalState.correctImageId == globalState.roundData.upvoteChoice.value) {
                if (debug) {
                    console.log("Right answer!");
                }
                $("#jtron").css({backgroundColor: "rgb(0, 225, 0)"});
    		} else {
        		if (debug) {
        		    console.log("Wrong answer!");
        		}
        		$("#jtron").css({backgroundColor: "rgb(225, 0, 0)"});
    		}
            
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
    
    $("#new-game").click(function(){
        $("#left-image").fadeOut(long_delay);        
        $("#right-image").fadeOut(long_delay);
        $("#caption-subreddit").fadeOut(long_delay);
        $("#caption-left").fadeOut(long_delay);
        $("#caption-right").fadeOut(long_delay);
        $("#result-left").fadeOut(long_delay);
        $("#result-right").fadeOut(long_delay);
    
        var postData = {user_id: globalState.user_id};
        
        if (debug) {
            console.log("New game. Sending data to server:");
            console.log(postData);
        }
                
        __loadPair(globalState, postData, preferQuestion);
    });
    
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