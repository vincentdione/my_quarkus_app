import subprocess

def run_pipeline_script(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DOCKER_IMAGE_NAME, DOCKER_IMAGE_TAG, DOCKER_REGISTRY):
    # Configure non-interactive frontend for tzdata
    subprocess.run(["export", "DEBIAN_FRONTEND=noninteractive"])
    subprocess.run(["ln", "-fs", "/usr/share/zoneinfo/Etc/UTC", "/etc/localtime"])
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "tzdata"])
    subprocess.run(["dpkg-reconfigure", "--frontend", "noninteractive", "tzdata"])

    # Installer et démarrer PostgreSQL
    print(" -------------------------------- INSTALLATION POSTGRES ---------------------------------")
    print(f"POSTGRES_USER: {POSTGRES_USER}")
    print(f"POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")
    print(f"POSTGRES_DB: {POSTGRES_DB}")
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", "postgresql"])
    # subprocess.run(["service", "postgresql", "start", "&", "sleep", "10"])
    # subprocess.run(["sudo", "-u", "postgres", "psql", "-c", f"CREATE USER {POSTGRES_USER} WITH ENCRYPTED PASSWORD '{POSTGRES_PASSWORD}';"])
    # subprocess.run(["sudo", "-u", "postgres", "psql", "-c", f"CREATE DATABASE {POSTGRES_DB} OWNER {POSTGRES_USER};"])

    # Installer JDK et Docker
    print(" -------------------------------- INSTALLATION JDK DOCKER ---------------------------------")
    subprocess.run(["apt-get", "install", "-y", "curl", "openjdk-17-jdk", "docker.io"])
    
    # Démarrer le démon Docker
    subprocess.run(["systemctl", "start", "docker"])
    subprocess.run(["sleep", "10"])

    # Lancer le conteneur PostgreSQL avec Docker
    subprocess.run(["docker", "run", "--name", "my_postgres", "-e", "POSTGRES_PASSWORD=postgres", "-e", f"POSTGRES_DB={POSTGRES_DB}", "-p", "5432:5432", "-d", "postgres"])
    subprocess.run(["sleep", "15"])

    # Mettre à jour application.properties pour Quarkus
    print(" --------------------------------  MISE A JOUR APPLICATION.PROPERTIES ---------------------------------")
    with open("source-code/src/main/resources/application.properties", "a") as prop_file:
        prop_file.write(f"quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/{POSTGRES_DB}\n")
        prop_file.write(f"quarkus.datasource.username={POSTGRES_USER}\n")
        prop_file.write(f"quarkus.datasource.password={POSTGRES_PASSWORD}\n")
        prop_file.write("quarkus.datasource.db-kind=postgresql\n")
        prop_file.write("quarkus.hibernate-orm.database.generation=update\n")

    # Installer Quarkus CLI
    print(" --------------------------------  INSTALLATION QUARKUS CLI ---------------------------------")
    subprocess.run(["curl", "-Ls", "https://github.com/quarkusio/quarkus/releases/download/2.13.3.Final/quarkus-cli-2.13.3.Final.tar.gz", "-o", "quarkus-cli.tar.gz"])
    subprocess.run(["tar", "-xzf", "quarkus-cli.tar.gz"])
    subprocess.run(["export", f"PATH=$PATH:{os.getcwd()}/quarkus-cli-2.13.3.Final/bin"])

    # Construire l'image Docker avec Quarkus CLI
    subprocess.run(["cd", "source-code"])
    java_home = subprocess.run(["readlink", "-f", "/usr/bin/java"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["export", f"JAVA_HOME={java_home}"])
    print(f"JAVA_HOME is set to {java_home}")
    print(" --------------------------------  BUILD IMAGE DOCKER ---------------------------------")
    subprocess.run(["quarkus", "build", "-Dquarkus.container-image.build=true", f"-Dquarkus.container-image.name={DOCKER_IMAGE_NAME}", f"-Dquarkus.container-image.tag={DOCKER_IMAGE_TAG}"])

    # Authentification au registre Docker
    subprocess.run(["echo", f"{DOCKER_TOKEN}", "|", "docker", "login", "-u", f"{DOCKER_USERNAME}", "--password-stdin", f"{DOCKER_REGISTRY}"])

    # Pousser l'image Docker vers le registre
    subprocess.run(["docker", "push", f"{DOCKER_IMAGE_NAME}:{DOCKER_IMAGE_TAG}"])

# Appel de la fonction avec les paramètres requis
run_pipeline_script(
    POSTGRES_USER="votre_utilisateur_postgres",
    POSTGRES_PASSWORD="votre_mot_de_passe_postgres",
    POSTGRES_DB="votre_base_de_donnees_postgres",
    DOCKER_IMAGE_NAME="votre_nom_image_docker",
    DOCKER_IMAGE_TAG="votre_tag_image_docker",
    DOCKER_REGISTRY="https://index.docker.io/v1/"
)
