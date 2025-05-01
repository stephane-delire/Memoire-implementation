/*
Action de l'éditeur, envoyer le contenu de l'éditeur
ou la suppression.
*/

const EditorExecuteBtn = document.getElementById("btn_execute");
const EditorDeleteBtn = document.getElementById("btn_reset");

const noResult = document.getElementById("no_result");
const resultContainer = document.getElementById("result_container");

// Reset
EditorDeleteBtn.addEventListener("click", function () {
    Editor.value = "";
    resultContainer.style.display = "none";
    noResult.style.display = "";
});

EditorExecuteBtn.addEventListener("click", function () {
    const query = Editor.value;
    if (query === "") {
        Editor.style.outline = "1px solid red";
        // add the animation shake
        Editor.style.animation = "shake 0.1s";
        setTimeout(() => {
            Editor.style.animation = "";
        }, 750);
    
    } else {
        Editor.style.outline = "none";
        //post the query to the server on /cqa
        fetch("/cqa", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Secret" : "@zeer-sdf-zertik-234kj"
            },
            body: JSON.stringify({ query })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Network response was not ok");
            }
        })
        .then(data => {
            // Display the result
            resultContainer.style.display = "";
            noResult.style.display = "none";
            
            console.log(data);

            // guarded
            document.getElementById('result_gardee').innerHTML = data.guarded[0];
            document.getElementById('result_gardee_2').innerHTML = data.guarded[1];

            // Graphe txt
            document.getElementById('result_graphe').innerHTML = data.graph_txt.replace(/\n/g, '<br>');
            // Graphe png
            document.getElementById('result_graphe_png').src = "data:image/png;base64," + data.graph_png;

            //cycle
            document.getElementById('result_cycle').innerHTML = data.cycle;


        });
    }
});