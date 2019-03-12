FROM superset-node-cache AS superset-node-cache
FROM superset-py-cache AS superset-py-cache

# -----------------------------------------------------------------------------
# Used for the JS builds
# -----------------------------------------------------------------------------
FROM superset-node-base AS superset-compile
WORKDIR /home/superset/superset_repo/superset/assets
COPY --from=superset-node-cache /root/.npm /root/.npm
WORKDIR /home/superset/
COPY . superset_repo
WORKDIR /home/superset/superset_repo/superset/assets
COPY --from=superset-node-cache /home/superset/superset_repo/superset/assets/.terser-plugin-cache/ /home/superset/superset_repo/superset/assets/.terser-plugin-cache/
RUN npm ci && npm run build && rm -rf ./node_modules

# -----------------------------------------------------------------------------
# Used to pack the python app with compiled JS in site-packages
# -----------------------------------------------------------------------------
FROM superset-py-cache AS superset-pack-python
WORKDIR /home/superset/
COPY --from=superset-compile /home/superset/superset_repo/superset/assets/dist/ superset_repo/superset/assets/dist/
COPY . superset_repo
RUN pip --no-cache-dir install superset_repo/

# -----------------------------------------------------------------------------
# Final lean image
# -----------------------------------------------------------------------------
FROM superset-base AS superset-final
COPY --from=superset-pack-python /usr/lib/python3.6/site-packages/ /usr/lib/python3.6/site-packages/

# Copying site-packages doesn't move the CLIs, so let's copy them one by one
COPY --from=superset-pack-python /usr/bin/superset /usr/bin/superset
COPY --from=superset-py-cache /usr/bin/gunicorn /usr/bin/gunicorn
COPY --from=superset-py-cache /usr/bin/celery /usr/bin/celery
COPY --from=superset-py-cache /usr/bin/fabmanager /usr/bin/fabmanager

COPY --chown=superset:superset ./superset_config.py /home/superset/pythonpath/
ENV PYTHONPATH=/home/superset/pythonpath

USER superset
WORKDIR /home/superset/
COPY ./docker-entrypoint.sh entrypoint.sh
EXPOSE 8088
ENTRYPOINT ["./entrypoint.sh"]
