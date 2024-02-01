## Setup enviroument variables NEO4J_LOGIN and NEO4J_PASSWORD
If you are using python-venv you can do this like this
As explained in https://stackoverflow.com/a/38645983
edit `/bin/activate`
### Unset variables
deactivate () {
    ...
    # Unset My Server's variables
    unset NEO4J_LOGIN
    unset NEO4J_PASSWORD
}
### Set variables
Then at the end of the activate script, set the vari1ables:

export NEO4J_LOGIN="neo4j"
export NEO4J_PASSWORD="test"

## Run neo4j docker
`docker run \
    --name testneo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/test \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4JLABS_PLUGINS='["apoc","graph-data-science"]' \
    neo4j:4.4.7`

    `neo4j:4.4.7 changed from neo4j:latest` because didn't have maching version in https://graphdatascience.ninja/versions.json


    
### Configure vscode to run python file as module
From this link https://stackoverflow.com/a/75772279
For example I call files like this
```python -m clustering.label_propagation```
To be able to use shared methods as this:
```from shared.utils import load_env_variables```
To configure vscode like this I needed to download vscode command-variable extension and add such configuration:
```json
 {
            "name": "Python: As Module",
            "type": "python",
            "request": "launch",
            "module": "${command:extension.commandvariable.file.relativeFileDotsNoExtension}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
```
And then in settings.json add 
"jupyter.notebookFileRoot": "${workspaceFolder}"