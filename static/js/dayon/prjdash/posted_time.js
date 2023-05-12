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
    initState(); // Initializes state variable (does not reinitialize on multiple calls)
    initDom(); // Loads relevant DOM elements into state variable for quick manipulation
    loadState();
    initControls(); // Connects all related elements to their functions
    processState();
});

var tb = {};

// Initializing page state variable
function initState() {
    if (document.state === undefined){
        document.state = {};
    };
    // Toolbar state
    if (document.state.toolbar === undefined){
        document.state.toolbar = {};
    };
    tb = document.state.toolbar;

    // add line
    if (tb.add === undefined){
        tb.add = {};
    };
    if (tb.add.modified === undefined){
        tb.add.modified = false;
    };
    if (tb.add.dom === undefined){
        tb.add.dom = {};
    };

    // filters
    if (tb.filters === undefined){
        tb.filters = {};
    };

    if (tb.filters.dom === undefined){
        tb.filters.dom = {};
    };

    // move line to another project
    if (tb.move === undefined){
        tb.move = {};
    };
    if (tb.move.dom === undefined){
        tb.move.dom = {};
    };

    // print current view
    if (tb.print === undefined){
        tb.print = {};
    };
    if (tb.print.dom === undefined){
        tb.print.dom = {};
    };

    // params
    if (document.state.params === undefined){
        document.state.params = {};
    };
    if (document.state.params.filters === undefined) {
        document.state.params.filters = {};
    };
    dpf = document.state.params.filters;
    if (dpf.dateFrom === undefined) {
        dpf.dateFrom = null;
    };
    if (dpf.dateTo === undefined) {
        dpf.dateTo = null;
    };
    if (dpf.employees === undefined) {
        dpf.employees = null;
    };
    if (dpf.items === undefined) {
        dpf.items = null;
    };

    return true;
};

function initDom() {
    //add line
    tb.add.dom.tab = document.getElementById('tbAddLine');
    tb.add.dom.page = document.getElementById('tdlg-add');
    tb.add.dom.form = document.getElementById('toolAddLine');
    // filters
    tb.filters.dom.tab = document.getElementById('tbFilters');
    tb.filters.dom.tab.filterOn = false;
    tb.filters.dom.page = document.getElementById('tdlg-filters');

    // move line to another project
    tb.move.dom.tab = document.getElementById('tbMoveLn');
    tb.move.dom.page = document.getElementById('tdlg-moveln');
    // print current view
    tb.print.dom.tab = document.getElementById('tbPrint');
    tb.print.dom.page = document.getElementById('tdlg-print');
};

function loadState(){
    // ??? Loading page state (from JSON object or cookies)
    // JSON object may be rendered to the page through a django template
    tb.add.active = false;
    tb.filters.active = false;
    tb.move.active = false;
    tb.print.active = false;

    processFieldErrors();

    // transfer filter values from page parameters to state.toolbar variable
    dpf = document.state.params.filters;
    f = document.state.toolbar.filters;
    f.props = {};
    fp = f.props;
    fp.date_from = dpf.dateFrom;
    fp.date_to = dpf.dateTo;
    fp.employee_ids = dpf.employees;
    fp.item_ids = dpf.items;
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
    //Events
    tb.add.dom.tab.onclick = tbAddClick;
    tb.filters.dom.tab.onclick = tbFiltersClick;
    tb.move.dom.tab.onclick = tbMoveClick;
    tb.print.dom.tab.onclick = tbPrintClick;

    //Put filter values into filter fields
    paramfl = document.state.params.filters;
    $("#datepicker-from").datepicker("setDate", paramfl.dateFrom);
    $("#datepicker-to").datepicker("setDate", paramfl.dateTo);
    if (paramfl.employees != '') {
        $("#select-employees").val(paramfl.employees.split(',')).trigger("change");
    };
    if (paramfl.items != '') {
        $("#select-tasks").val(paramfl.items.split(',')).trigger("change");
    };
    //Check if any filter is on
    tb.filters.dom.tab.filterOn = (paramfl.dateFrom != '' || paramfl.dateTo != '' || paramfl.employees != '' || paramfl.items != '');
    //If any of the filters are on then show checkbox beside the filter icon
    if (tb.filters.dom.tab.filterOn){
        $("#filter_on").show();
    };
    //Add form action (to preserve active filters on save and refresh)
    //document.toolAddLine.action = getUrl(); //window.location.href; -- not effective

    // transfer filter values from page parameters to the hidden fields of add new record form (to pass filter parameters on POST request)
    dpf = document.state.params.filters;
    document.getElementById('filter_dateFrom').value = dpf.dateFrom;
    document.getElementById('filter_dateTo').value = dpf.dateTo;
    document.getElementById('filter_emplIds').value = dpf.employees;
    document.getElementById('filter_itemIds').value = dpf.items;
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
};

function getFilterUrl(urlBase){
    /* Building URL with filters */
    resUrl = '';
    qm = '';
    fp = document.state.toolbar.filters.props;

    if (fp.date_from && fp.date_to) {
        resUrl = urlBase + "?date-from=" + fp.date_from + "&date-to=" + fp.date_to;
    }
    else if (fp.date_from) {
        resUrl = urlBase + "?date-from=" + fp.date_from;
    }
    else if (fp.date_to) {
        resUrl = urlBase + "?date-to=" + fp.date_to;
    }
    else {
        resUrl = urlBase;
        qm = '?';
    };
    if (fp.employee_ids != null && fp.employee_ids.length > 0) {
        resUrl = resUrl + qm + "&employees=" + fp.employee_ids;
        qm = '';
    };
    if (fp.item_ids != null && fp.item_ids.length > 0) {
        resUrl = resUrl + qm + "&items=" + fp.item_ids;
    };
    return resUrl;
};

function getUrl(){
    return getFilterUrl(document.state.params.urlBase);
};
