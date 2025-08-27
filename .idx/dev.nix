# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    # pkgs.go
    pkgs.python311
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.python-multipart
    pkgs.python311Packages.sqlalchemy
    pkgs.python311Packages.psycopg2
    pkgs.python311Packages.alembic
    pkgs.python311Packages.pydantic
    pkgs.python311Packages.pydantic-settings
    pkgs.python311Packages.python-jose
    pkgs.python311Packages.passlib
    pkgs.python311Packages.supabase
    pkgs.python311Packages.postgrest
    pkgs.python311Packages.pandas
    pkgs.python311Packages.numpy
    pkgs.python311Packages.openpyxl
    pkgs.python311Packages.xlsxwriter
    pkgs.python311Packages.plotly
    pkgs.python311Packages.kaleido
    pkgs.python311Packages.jinja2
    pkgs.python311Packages.scikit-learn
    pkgs.python311Packages.xgboost
    pkgs.python311Packages.lightgbm
    pkgs.python311Packages.imbalanced-learn
    pkgs.python311Packages.optuna
    pkgs.python311Packages.shap
    pkgs.python311Packages.joblib
    pkgs.python311Packages.firebase-admin
    pkgs.python311Packages.pyrebase4
    pkgs.python311Packages.google-cloud-bigquery
    pkgs.python311Packages.google-cloud-storage
    pkgs.python311Packages.google-cloud-aiplatform
    pkgs.python311Packages.redis
    pkgs.python311Packages.celery
    pkgs.python311Packages.aiofiles
    pkgs.python311Packages.httpx
    pkgs.python311Packages.python-dotenv
    pkgs.python311Packages.structlog
    # pkgs.python311Packages.pip # No need to explicitly add pip if python311 is added
    # pkgs.nodejs_20
    # pkgs.nodePackages.nodemon
  ];

  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Example: install JS dependencies from NPM
        # npm-install = "npm install";
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # watch-backend = "npm run watch-backend";
      };
    };
  };
}
