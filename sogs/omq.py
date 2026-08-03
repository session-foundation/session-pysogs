# Common oxenmq object; this is used by workers and the oxenmq mule.  We create, but do not start,
# this pre-forking.

import oxenmq
from oxenc import bt_serialize

from . import crypto, config
from .postfork import postfork

omq = None
mule_conn = None
test_suite = False


def make_omq():
    omq = oxenmq.OxenMQ(privkey=crypto._privkey.encode(), pubkey=crypto.server_pubkey.encode())

    # We have multiple workers talking to the mule, so we *must* use ephemeral ids to not replace
    # each others' connections.
    omq.ephemeral_routing_id = True

    return omq


# Postfork for workers: we start oxenmq and connect to the mule process
@postfork
def start_oxenmq():
    try:
        import uwsgi
    except ModuleNotFoundError:
        return

    global omq, mule_conn

    omq = make_omq()

    if uwsgi.mule_id() != 0:
        from . import mule

        mule.setup_omq()
        return

    from .web import app  # Imported here to avoid circular import

    worker_id = uwsgi.worker_id()

    app.logger.debug(f"Starting oxenmq connection to mule in worker {worker_id}")

    omq.start()
    app.logger.debug("Started, connecting to mule")

    def mule_connected(conn):
        app.logger.debug(f"worker {worker_id} connected to mule OMQ")

    def mule_connect_failed(conn, reason):
        app.logger.error(f"worker {worker_id} could not connect to the mule: {reason}")

    # Connect asynchronously: uwsgi starts workers and the mule at the same time and does not order
    # them, so a worker that gets there first would find nothing listening on the internal socket
    # yet.  This form returns a usable connection immediately and queues anything we send until the
    # mule is up, rather than giving up on a mule that is a moment behind us.
    mule_conn = omq.connect_remote(
        oxenmq.Address(config.OMQ_INTERNAL), mule_connected, mule_connect_failed
    )


def send_mule(command, *args, prefix="worker."):
    """
    Sends a command to the mule from a worker (or possibly from the mule itself).  The command will
    be prefixed with "worker." (unless overridden).

    Any args will be bt-serialized and send as message parts.
    """
    if prefix:
        command = prefix + command

    if test_suite and omq is None:
        pass  # TODO: for mule call testing we may want to do something else here?
    else:
        omq.send(mule_conn, command, *(bt_serialize(data) for data in args))
