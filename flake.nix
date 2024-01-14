# nix/flake.nix
#
# This file packages basics-pytorch as a Nix flake.
#
# Copyright (C) 2023-today rydnr's rydnr/basics-pytorch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
{
  description =
    "testcontainers-python facilitates the use of Docker containers for functional and integration testing.";
  inputs = rec {
    flake-utils.url = "github:numtide/flake-utils/v1.0.0";
    nixos.url = "github:NixOS/nixpkgs/23.11";
    esdbclient = {
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixos.follows = "nixos";
      url = "github:rydnr/nix-flakes?dir=esdbclient";
    };
  };
  outputs = inputs:
    with inputs;
    let
      defaultSystems = flake-utils.lib.defaultSystems;
      supportedSystems = if builtins.elem "armv6l-linux" defaultSystems then
        defaultSystems
      else
        defaultSystems ++ [ "armv6l-linux" ];
    in flake-utils.lib.eachSystem supportedSystems (system:
      let
        org = "rydnr";
        repo = "testcontainers-python";
        version = "0.0.1";
        pname = "${org}-${repo}";
        description =
          "testcontainers-python facilitates the use of Docker containers for functional and integration testing.";
        homepage = "https://github.com/testcontainers/testcontainers-python";
        maintainers = [ "rydnr <github@acm-sl.org>" ];
        pkgs = import nixos { inherit system; };
        shared = import "${pythoneda-shared-pythoneda-banner}/nix/shared.nix";
        rydnr-testcontainers-python-for = { esdbclient, python }:
          let
            pythonVersionParts = builtins.splitVersion python.version;
            pythonMajorVersion = builtins.head pythonVersionParts;
            pythonMajorMinorVersion =
              "${pythonMajorVersion}.${builtins.elemAt pythonVersionParts 1}";
          in pkgs.stdenv.mkDerivation rec {
            name = "testcontainers-python";
            src = ./.;

            buildInputs = with python.pkgs; [
              pkgs.gnumake
              python
              setuptools
              twine
              wheel
            ];

            propagatedBuildInputs = with python.pkgs; [
              azure-storage-blob
              boto3
              clickhouse-driver
              # cx_Oracle
              docker
              esdbclient
              google-cloud-pubsub
              kafka-python
              kubernetes
              minio
              neo4j
              opensearch-py
              pika
              psycopg2
              pymongo
              # pymssql
              pymysql
              python-arango
              python-keycloak
              pyyaml
              redis
              selenium
              sqlalchemy
              urllib3
              wrapt
            ];

            buildPhase = "make dist";
            installPhase = ''
              mkdir -p $out/dist $out/lib/python${pythonMajorMinorVersion}/site-packages/testcontainers;
              for m in $(find . -maxdepth 1 -type d | grep -v .git | grep -v requirements | grep -v '.devcontainer' | grep -v 'doctests' | grep -v '^.$'); do
                cp -r $m/dist $out/dist/$m;
                [[ -e $m/build/lib/testcontainers/$m ]] && cp -r $m/build/lib/testcontainers/$m $out/lib/python${pythonMajorMinorVersion}/site-packages/testcontainers/;
              done
            '';

            meta = with pkgs.lib; {
              license = licenses.gpl3;
              inherit description homepage maintainers;
            };
          };
      in rec {
        defaultPackage = packages.default;
        packages = rec {
          default = rydnr-testcontainers-python-default;
          rydnr-testcontainers-python-default =
            rydnr-testcontainers-python-python311;
          rydnr-testcontainers-python-python38 =
            rydnr-testcontainers-python-for {
              esdbclient = esdbclient.packages.${system}.esdbclient-python38;
              python = pkgs.python38;
            };
          rydnr-testcontainers-python-python39 =
            rydnr-testcontainers-python-for {
              esdbclient = esdbclient.packages.${system}.esdbclient-python39;
              python = pkgs.python39;
            };
          rydnr-testcontainers-python-python310 =
            rydnr-testcontainers-python-for {
              esdbclient = esdbclient.packages.${system}.esdbclient-python310;
              python = pkgs.python310;
            };
          rydnr-testcontainers-python-python311 =
            rydnr-testcontainers-python-for {
              esdbclient = esdbclient.packages.${system}.esdbclient-python311;
              python = pkgs.python311;
            };
        };
      });
}
