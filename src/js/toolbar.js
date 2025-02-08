//
//
//

// Constants
const toolbarDiv = document.querySelector('#toolbar');
const toolDesactivateConstraints = document.querySelector('#tool_deactivate_constraints');
const toolHideResults = document.querySelector('#tool_hide_res');
const toolHideTable = document.querySelector('#tool_hide_table');
const toolReset = document.querySelector('#tool_reset');
const toolHelp = document.querySelector('#tool_help');
const toolGithub = document.querySelector('#tool_github');


// Object
class toolbarObject {
    constructor() {
        this.desactivateConstraints = false;
        this.hideResults = false;
        this.hideTable = false;
        this.init();
    }
    init() {
        // remove from the tools the class 'active' if it exists
        let tools = toolbarDiv.querySelectorAll('.tool_btn');
        tools.forEach(tool => {
            tool.classList.remove('active');
        });
        // add the active class to the Desactivate Constraints tool
        toolDesactivateConstraints.classList.add('active');
        // add the event listeners to every tool
        toolDesactivateConstraints.addEventListener('click', this.desactivateConstraintsHandler.bind(this));
        toolHideResults.addEventListener('click', this.hideResultsHandler.bind(this));
        toolHideTable.addEventListener('click', this.hideTableHandler.bind(this));
        toolReset.addEventListener('click', this.resetHandler.bind(this));
        toolHelp.addEventListener('click', this.helpHandler.bind(this));
        toolGithub.addEventListener('click', this.githubHandler.bind(this));
    }
    
    // Event Handlers
    desactivateConstraintsHandler() {
        this.desactivateConstraints = !this.desactivateConstraints;
        if (this.desactivateConstraints) {
            toolDesactivateConstraints.classList.remove('active');
        } else {
            toolDesactivateConstraints.classList.add('active');
        }
    }
    hideResultsHandler() {
        this.hideResults = !this.hideResults;
        if (this.hideResults) {
            toolHideResults.classList.add('active');
            const resultPanel = document.querySelector('#res_panel');
            resultPanel.style.display = 'none';
        } else {
            toolHideResults.classList.remove('active');
            const resultPanel = document.querySelector('#res_panel');
            resultPanel.style.display = '';
        }
    }
    hideTableHandler() {
        this.hideTable = !this.hideTable;
        if (this.hideTable) {
            toolHideTable.classList.add('active');
            const tablePanel = document.querySelector('#table_panel');
            tablePanel.style.display = 'none';
        } else {
            toolHideTable.classList.remove('active');
            const tablePanel = document.querySelector('#table_panel');
            tablePanel.style.display = '';
        }
    }
    resetHandler() {
        window.location.reload();
    }
    helpHandler() {
        // TODO
        console.log('help');
    }
    githubHandler() {
        // https://github.com/stephane-delire/Memoire-implementation
        // redirect to the github page of the project
        // in new tab
        window.open('https://github.com/stephane-delire/Memoire-implementation', '_blank');
    }
}


// Toolbar object
let toolbar = new toolbarObject();
window.toolbar = toolbar;