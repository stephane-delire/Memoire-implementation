/*
Action de l'éditeur, envoyer le contenu de l'éditeur
ou la suppression.
*/

const EditorExecuteBtn = document.getElementById("btn_execute");
const EditorDeleteBtn = document.getElementById("btn_reset");

const noResult = document.getElementById("no_result");
const resultContainer = document.getElementById("result_container");

const emptySvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-circle-slash-icon lucide-circle-slash"><circle cx="12" cy="12" r="10"/><line x1="9" x2="15" y1="15" y2="9"/></svg>`;

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
            resultContainer.innerHTML = "";
            resultContainer.style.display = "";
            noResult.style.display = "none";

            // guarded
            const guardedDiv = document.createElement("div");
            guardedDiv.classList.add("res_panel");
            guardedDiv.setAttribute("id", "result_gardee");
            const title = document.createElement("span");
            title.classList.add("res_title");
            title.innerHTML = "Garde";
            guardedDiv.appendChild(title);
            const content = document.createElement("span");
            content.classList.add("res_content");
            content.innerHTML = data.guarded[0];
            if (data.guarded[0] == true) {
                content.classList.add("res_content_true");
            } else {
                content.classList.add("res_content_false");
            }
            guardedDiv.appendChild(content);
            const content2 = document.createElement("span");
            content2.classList.add("res_content");
            content2.innerHTML = data.guarded[1];
            if (data.guarded[0] == true) {
                content2.classList.add("res_content_true");
            } else {
                content2.classList.add("res_content_false");
            }
            if (content2.innerHTML == "WG") {
                content2.innerHTML = "Clique-guarded";
            }
            guardedDiv.appendChild(content2);
            var hr = document.createElement("hr");
            hr.classList.add("res_hr");
            resultContainer.appendChild(guardedDiv);
            resultContainer.appendChild(hr);

            // Graphe txt
            const grapheDiv = document.createElement("div");
            grapheDiv.classList.add("res_panel");
            grapheDiv.setAttribute("id", "result_graphe");
            const titleGraphe = document.createElement("span");
            titleGraphe.classList.add("res_title");
            titleGraphe.innerHTML = "Graphe txt";
            grapheDiv.appendChild(titleGraphe);
            const contentGraphe = document.createElement("span");
            contentGraphe.classList.add("res_content");
            if (data.graph_txt) {
                contentGraphe.innerHTML = data.graph_txt.replace(/\n/g, '<br>');
            } else {
                contentGraphe.innerHTML = emptySvg;
            }
            grapheDiv.appendChild(contentGraphe);
            var hr = document.createElement("hr");
            hr.classList.add("res_hr");
            resultContainer.appendChild(grapheDiv);
            resultContainer.appendChild(hr);

            // Graphe png
            const graphePngDiv = document.createElement("div");
            graphePngDiv.classList.add("res_panel");
            graphePngDiv.setAttribute("id", "result_graphe_png");
            const titleGraphePng = document.createElement("span");
            titleGraphePng.classList.add("res_title");
            titleGraphePng.innerHTML = "Graphe png";
            graphePngDiv.appendChild(titleGraphePng);
            const contentGraphePng = document.createElement("img");
            contentGraphePng.classList.add("res_content");
            if (data.graph_png) {
                contentGraphePng.src = "data:image/png;base64," + data.graph_png;
                contentGraphePng.alt = "Graphe png";
            } else {
                // if no graphe png, display the empty svg
                contentGraphePng.src = "data:image/svg+xml;base64," + btoa(emptySvg);
                contentGraphePng.alt = "Graphe png";
            }
            graphePngDiv.appendChild(contentGraphePng);
            var hr = document.createElement("hr");
            hr.classList.add("res_hr");
            resultContainer.appendChild(graphePngDiv);
            resultContainer.appendChild(hr);

            //cycle
            const cycleDiv = document.createElement("div");
            cycleDiv.classList.add("res_panel");
            cycleDiv.setAttribute("id", "result_cycle");
            const titleCycle = document.createElement("span");
            titleCycle.classList.add("res_title");
            titleCycle.innerHTML = "Cycle";
            cycleDiv.appendChild(titleCycle);
            const contentCycle = document.createElement("span");
            contentCycle.classList.add("res_content");
            if (data.cycle || data.cycle == false) {
                contentCycle.innerHTML = data.cycle;
                if (data.cycle == true) {
                    contentCycle.classList.add("res_content_false");
                } else {
                    contentCycle.classList.add("res_content_true");
                }
            }
            else {
                contentCycle.innerHTML = emptySvg;
            }
            if (contentCycle.innerHTML == "false") {
                contentCycle.innerHTML = "Acyclique";
            } else if (contentCycle.innerHTML == "true") {
                contentCycle.innerHTML = "Cyclique";
            }
            cycleDiv.appendChild(contentCycle);
            var hr = document.createElement("hr");
            hr.classList.add("res_hr");
            resultContainer.appendChild(cycleDiv);
            resultContainer.appendChild(hr);

            //certain
            const certainDiv = document.createElement("div");
            certainDiv.classList.add("res_panel");
            certainDiv.setAttribute("id", "result_certain");
            const titleCertain = document.createElement("span");
            titleCertain.classList.add("res_title");
            titleCertain.innerHTML = "Certitude";
            certainDiv.appendChild(titleCertain);
            const contentCertain = document.createElement("span");
            contentCertain.classList.add("res_content");
            if (data.certain || data.certain == false) {
                contentCertain.innerHTML = data.certain;
                if (data.certain == true) {
                    contentCertain.classList.add("res_content_true");
                } else {
                    contentCertain.classList.add("res_content_false");
                }
            } else {
                contentCertain.innerHTML = "Pas évalué";
            }
            certainDiv.appendChild(contentCertain);
            var hr = document.createElement("hr");
            hr.classList.add("res_hr");
            resultContainer.appendChild(certainDiv);
            resultContainer.appendChild(hr);

            // rewrited
            // const rewritedDiv = document.createElement("div");
            // rewritedDiv.classList.add("res_panel");
            // rewritedDiv.setAttribute("id", "result_rewrited");
            // const titleRewrited = document.createElement("span");
            // titleRewrited.classList.add("res_title");
            // titleRewrited.innerHTML = "Reécriture";
            // rewritedDiv.appendChild(titleRewrited);
            // const contentRewrited = document.createElement("span");
            // contentRewrited.classList.add("res_content");
            // if (data.rewrite) {
            //     contentRewrited.innerHTML = data.rewrite.replace(/\n/g, '<br>');
            // } else {
            //     contentRewrited.innerHTML = emptySvg;
            // }
            // rewritedDiv.appendChild(contentRewrited);
            // var hr = document.createElement("hr");
            // hr.classList.add("res_hr");
            // resultContainer.appendChild(rewritedDiv);
            // resultContainer.appendChild(hr);
            
            // latex
            if (data.latex) {
                const latexDiv = document.createElement("div");
                latexDiv.classList.add("res_panel");
                latexDiv.setAttribute("id", "result_latex");
                const titleLatex = document.createElement("span");
                titleLatex.classList.add("res_title");
                titleLatex.innerHTML = "Réécriture";
                latexDiv.appendChild(titleLatex);
                const contentLatex = document.createElement("span");
                contentLatex.classList.add("res_content");
                if (data.latex) {
                    contentLatex.innerHTML = "$" + data.latex.replace(/\n/g, '<br>') + "$";
                    contentLatex.classList.add("latex_content");
                }
                else {
                    contentLatex.innerHTML = emptySvg;
                    contentLatex.classList.add("latex_content_empty");
                }
                latexDiv.appendChild(contentLatex);
                var hr = document.createElement("hr");
                hr.classList.add("res_hr");
                resultContainer.appendChild(latexDiv);
                resultContainer.appendChild(hr);
                MathJax.typeset();

            }

            // Trace
            if (data.trace) {
                const traceDiv = document.createElement("div");
                traceDiv.classList.add("res_panel");
                traceDiv.setAttribute("id", "result_trace");

                const titleTrace = document.createElement("span");
                titleTrace.classList.add("res_title");
                titleTrace.innerHTML = "Trace";
                traceDiv.appendChild(titleTrace);

                const details = document.createElement("details");
                const summary = document.createElement("summary");
                summary.innerText = "Afficher la trace";
                details.appendChild(summary);

                const contentTrace = document.createElement("pre");
                contentTrace.classList.add("res_content");

                if (Array.isArray(data.trace)) {
                    contentTrace.innerText = data.trace.join("\n");
                } else {
                    contentTrace.innerText = data.trace || "";
                }

                details.appendChild(contentTrace);
                traceDiv.appendChild(details);

                const hr = document.createElement("hr");
                hr.classList.add("res_hr");

                resultContainer.appendChild(traceDiv);
                resultContainer.appendChild(hr);
            }


        });
    }
});