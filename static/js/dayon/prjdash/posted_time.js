/* ------ INITIALIZING SELECT2 -------*/
$(document).ready(function() {
    $('.js-s2').select2({
        closeOnSelect: false,
        width: "300px",
    });
});

/* ------ Initializing Datepickers ------ */
$( function() {
    $.datepicker.setDefaults($.datepicker.regional["lt"]);
    //$( "#datepicker-from" ).datepicker({maxDate: "+1D", onSelect: set_date_from});
    $( "#datepicker-from" ).datepicker({maxDate: "+1D"});
} );

$( function() {
    $.datepicker.setDefaults($.datepicker.regional["lt"]);	  	  
    //$( "#datepicker-to" ).datepicker({maxDate: "+1D", onSelect: set_date_to});
    $( "#datepicker-to" ).datepicker({maxDate: "+1D"});
} );

// ------ initialize page ------ */
$(function() {
    initState();
    loadState();
    initControls();
    processState();
});

var tb = {};

// Initializing page state variable
function initState() {
    document.state = {};
    // Toolbar state

    document.state.toolbar = {};
    tb = document.state.toolbar;

    // add line
    tb.add = {};
    tb.add.modified = false;
    tb.add.dom = {};
    tb.add.dom.tab = document.getElementById('tbAddLine');
    tb.add.dom.page = document.getElementById('tdlg-add');

    // filters
    tb.filters = {};
    tb.filters.dom = {};
    tb.filters.dom.tab = document.getElementById('tbFilters');
    tb.filters.dom.page = document.getElementById('tdlg-filters');

    // move line to another project
    tb.move = {};
    tb.move.dom = {};
    tb.move.dom.tab = document.getElementById('tbMoveLn');
    tb.move.dom.page = document.getElementById('tdlg-moveln');

    // print current view
    tb.print = {};
    tb.print.dom = {};
    tb.print.dom.tab = document.getElementById('tbPrint');
    tb.print.dom.page = document.getElementById('tdlg-print');

    return true;
};

function loadState(){
    // ??? Loading page state (from JSON object or cookies)
    // JSON object may be rendered to the page through a django template
    tb.add.active = false;
    tb.filters.active = false;
    tb.move.active = false;
    tb.print.active = false;
    processFieldErrors();
};

// Processing page state.
// Runs after each page element event which is changing the page state.
function processState(){
    // Processing toolbar state
    // Updates all controls according to the page state
    function processToolbarState() {
        // Updating toolbar controls
        if (tb.add.active == true) {
            tb.add.dom.tab.classList.add("active");
            tb.add.dom.page.classList.remove("hidden");
        } else {
            tb.add.dom.tab.classList.remove("active");
            tb.add.dom.page.classList.add("hidden");
        };
        if (tb.filters.active == true) {
            tb.filters.dom.tab.classList.add("active");
            tb.filters.dom.page.classList.remove("hidden");
        } else {
            tb.filters.dom.tab.classList.remove("active");
            tb.filters.dom.page.classList.add("hidden");
        };
        if (tb.move.active == true) {
            tb.move.dom.tab.classList.add("active");
            tb.move.dom.page.classList.remove("hidden");
        } else {
            tb.move.dom.tab.classList.remove("active");
            tb.move.dom.page.classList.add("hidden");
        };
        if (tb.print.active == true) {
            tb.print.dom.tab.classList.add("active");
            tb.print.dom.page.classList.remove("hidden");
        } else {
            tb.print.dom.tab.classList.remove("active");
            tb.print.dom.page.classList.add("hidden");
        };
        return true;
    };
    return processToolbarState();
};

// Connects all related elements to their functions
function initControls(){
    tb.add.dom.tab.onclick = tbAddClick;
    tb.filters.dom.tab.onclick = tbFiltersClick;
    tb.move.dom.tab.onclick = tbMoveClick;
    tb.print.dom.tab.onclick = tbPrintClick;
};

//Event functions
function tbAddClick(){
    // On tab button "ADD" click
    tb.add.active = !tb.add.active;
    tb.filters.active = false;
    tb.move.active = false;
    tb.print.active = false;
    processState();
};

function tbFiltersClick(){
    // On tab button "FILTERS" click
    tb.filters.active = !tb.filters.active;
    tb.add.active = false;
    tb.move.active = false;
    tb.print.active = false;
    processState();
};

function tbMoveClick(){
    // On tab button "MOVE" click
    tb.move.active = !tb.move.active;
    tb.add.active = false;
    tb.filters.active = false;
    tb.print.active = false;
    processState();
};

function tbPrintClick(){
    // On tab button "PRINT" click
    tb.print.active = !tb.print.active;
    tb.add.active = false;
    tb.filters.active = false;
    tb.move.active = false;
    processState();
};

function processFieldErrors(){
    // Detect if there were errors;
    // If so, open the tab containing the error;
    // Style the error
    tbFields = document.getElementsByClassName('tool-field');
    for (const tbField of tbFields){
        const subFldDivs = tbField.querySelectorAll('div');
        // searching for error <ul>
        for (const subFldDiv of subFldDivs){
            let ulErrorEl = subFldDiv.querySelectorAll("ul.errorlist");
            if (ulErrorEl.length > 0){
                //Error found. Processing
                switch (tbField.dataset.tab){ // Activating relevant tab
                    case "add": 
                        tb.add.modified = true; //if error then setting initial page state as modified
                        tb.add.active = true;
                        break;
                    case "move":
                        tb.move.active = true;
                        break;
                    case "filters":
                        tb.filters.active = true;
                        break;
                    case "print":
                        tb.print.active = true;
                        break;
                };
                // Setting style to the field to highlight the error
                tbField.classList.remove('ok');
                tbField.classList.add('error');
                //Creating error box element and putting error messages into it
                const errorBox = document.createElement("div");
                errorBox.classList.add('error-box');
                for (ulError of ulErrorEl){
                    ulError.classList.remove("errorlist"); //removing the original styling of the error message
                    ulError.classList.add('errortext') //adding new styling for the error message
                    errorBox.appendChild(ulError);
                }
                tbField.parentNode.insertBefore(errorBox, tbField);
                processState();
            };

        };
    };
/*
function get_filter_url(){
    resUrl = '';
    qm = '';
        if (document.props.date_from && document.props.date_to) {
            resUrl = "{% url 'pdash-time-review' location='desktop' project_id=project.id %}?date-from=" + document.props.date_from + "&date-to=" + document.props.date_to;
-       }
        else if (document.props.date_from) {
            resUrl = "{% url 'pdash-time-review' location='desktop' project_id=project.id %}?date-from=" + document.props.date_from;
        }
        else if (document.props.date_to) {
            resUrl = "{% url 'pdash-time-review' location='desktop' project_id=project.id %}?date-to=" + document.props.date_to;
        }
        else {
            resUrl = "{% url 'pdash-time-review' location='desktop' project_id=project.id %}";
            qm = '?';
        };
        if (document.props.employee_ids != null && document.props.employee_ids.length > 0) {
            resUrl = resUrl + qm + "&employees=" + document.props.employee_ids;
            qm = '';
        };
        if (document.props.item_ids != null && document.props.item_ids.length > 0) {
            resUrl = resUrl + qm + "&items=" + document.props.item_ids;
        };
        return resUrl;
    };
*/
};
