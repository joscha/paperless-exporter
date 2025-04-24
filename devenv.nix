{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:

{
  overlays = [
    (final: prev: {
      uv =
        (import inputs.nixpkgs-unstable {
          system = prev.stdenv.system;
        }).uv;
    })
  ];

  # https://devenv.sh/packages/
  packages =
    [
      pkgs.git
      pkgs.python312Packages.setuptools
    ]
    ++ lib.optionals pkgs.stdenv.isDarwin [
      pkgs.terminal-notifier
    ];

  languages.python.enable = true;
  languages.python.uv.enable = true;
  languages.python.uv.sync.enable = true;
  languages.python.uv.sync.allExtras = true;
  languages.python.venv.enable = true;
  languages.python.version = "3.12";

  scripts.build.exec = ''
    uv build
  '';

  scripts.generate-models.exec = ''
    pushd $DEVENV_ROOT/fixtures/library.paperless >/dev/null
    pwiz.py -e sqlite DocumentWallet.documentwalletsql > ../../src/model.py
    popd >/dev/null
  '';

  scripts.format.exec = ''
    yamlfmt .
    markdownlint --fix .
    pre-commit run --all-files
  '';

  scripts.test-all.exec = ''
    pytest -s -vv "$@"
  '';

  scripts.test-update-snapshots.exec = ''
    pytest --snapshot-update "$@"
  '';

  scripts.test-watch.exec = ''
    ptw --onpass "terminal-notifier -message \"Tests passed\" -title \"✅\"" \
      --onfail "terminal-notifier -message \"Tests failed\" -title \"❌\""
  '';

  # https://devenv.sh/tests/
  enterTest = ''
    test-all
  '';

  git-hooks.hooks = {
    shellcheck.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
    typos.enable = true;
    yamllint.enable = true;
    yamlfmt.enable = true;
    yamlfmt.settings.lint-only = false;
    check-toml.enable = true;
    commitizen.enable = true;
    nixfmt-rfc-style.enable = true;
    mdformat.enable = true;
    mdformat.package = pkgs.mdformat.withPlugins (
      ps: with ps; [
        mdformat-frontmatter
      ]
    );
    mdformat.excludes = [
      "fixtures/out/.*"
    ];
    markdownlint.enable = true;
    markdownlint.excludes = [
      "fixtures/out/.*\.md"
    ];
  };

}
