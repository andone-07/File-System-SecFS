class Principal:
    @property
    def id(self):
        return -1
    def is_user(self):
        return False
    def is_group(self):
        return False

class User(Principal):
    def __init__(self, uid):
        if not isinstance(uid, int):
            raise TypeError("id {} is not an int, is a {}".format(uid, type(uid)))

        self._uid = uid
    def __getstate__(self):
        return (self._uid, False)
    def __setstate__(self, state):
        self._uid = state[0]
    @property
    def id(self):
        return self._uid
    def is_user(self):
        return True
    def __eq__(self, other):
        return isinstance(other, User) and self._uid == other._uid
    def __str__(self):
        return "<uid={}>".format(self._uid)
    def __hash__(self):
        return hash(self._uid)

class Group(Principal):
    def __init__(self, gid):
        if not isinstance(gid, int):
            raise TypeError("id {} is not an int, is a {}".format(gid, type(gid)))

        self._gid = gid
    def __getstate__(self):
        return (self._gid, True)
    def __setstate__(self, state):
        self._gid = state[0]
    @property
    def id(self):
        return self._gid
    def is_group(self):
        return True
    def __eq__(self, other):
        return isinstance(other, Group) and self._gid == other._gid
    def __str__(self):
        return "<gid={}>".format(self._gid)
    def __hash__(self):
        return hash(self._gid)

class I:
    def __init__(self, principal, inumber=None):
        if not isinstance(principal, Principal):
            raise TypeError("{} is not a Principal, is a {}".format(principal, type(principal)))
        if inumber is not None and not isinstance(inumber, int):
            raise TypeError("inumber {} is not an int, is a {}".format(inumber, type(inumber)))

        self._p = principal
        self._n = inumber
    def __getstate__(self):
        return (self._p, self._n)
    def __setstate__(self, state):
        self._p = state[0]
        self._n = state[1]
    @property
    def p(self):
        return self._p
    @property
    def n(self):
        return self._n
    def allocate(self, inumber):
        if self._n is not None:
            raise AssertionError("tried to re-allocate allocated I {} with inumber {}".format(self, inumber))
        self._n = inumber
    def allocated(self):
        return self._n is not None
    def __eq__(self, other):
        return isinstance(other, I) and self._p == other._p and self._n == other._n
    def __str__(self):
        if self.allocated():
            return "({}, {})".format(self._p, self._n)
        return "({}, <unallocated>)".format(self._p)
    def __hash__(self):
        if not self.allocated():
            raise TypeError("cannot hash unallocated i {}".format(self))
        return hash((self._p, self._n))
class VersionStructure:
    def __init__(self):
        self._ihandle = None
        self._gihandles = {}
        self._version = {}
        self.signature = None

    def update_version(self, principal, version):
        self._version[principal] = version
    
    def update_ihandle(self, ihandle):
        self._ihandle = ihandle
    
    def update_group_ihandle(self, principal, ihandle):
        self._gihandles[principal] = ihandle
    
    @property
    def ihandle(self):
        return self._ihandle

    @property
    def gihandles(self):
        return self._gihandles

    def get_version(self, u):
        if u in self._version:
            return self._version[u]
        else:
            return 0

    def bytes(self):
        import pickle
        return pickle.dumps([self._ihandle, self._gihandles])

class VS:
    def __init__(self, user=None):
        # The i-handle of the VS user
        self.ihandle = None

        # The User's identifier
        self.user = user

        #List of group i-handles for the user
        self.group_ihandle = {}

        #version vector
        #Dictionary of version numbers of users an groups as last seen by the user
        self.v_vect = {}

        #Signature of user
        self.signature = None
    

class VSL:
    def __init__(self, p_vsl={}):
        # List of VS's keyed by principal
        self.vsl = p_vsl

    # Fetch the current VS for a specified user
    def fetch_VS(self, principal):
        return self.vsl[principal]

    def update_VS(self, principal, vs):
        # sign VS before updating
        import pickle
        key = secfs.crypto.keys[vs.user]
        vs.signature = secfs.crypto.sign(key, pickle.dumps(vs))
        # check for prev <= current
        old_vs = VS()
        if principal in self.vsl.keys():
            old_vs = self.vsl[principal]
        old_total = sum(old_vs.v_vect.values())
        new_total = sum(vs.v_vect.values())
        assert new_total >= old_total
        self.vsl[principal] = vs

    ## TODO figure out if we still need this function?
    def serialize(self):
        for key in self.vsl.keys():
            vs = self.vsl[key]
            ser = vs.serialize()
            self.vsl[key] = ser

    def find_group_versions(self):
        ret_versions = {}
        ret_handles = {}
        for vs in self.vsl.values():
            for g in vs.group_ihandle:
                g_version = vs.v_vect[g]
                g_handle = vs.group_ihandle[g]

                if g not in ret_versions or g_version > ret_versions[g]:
                    # THis is a more current version than the one we have stored
                    ret_versions[g] = g_version
                    ret_handles[g] = g_handle
        return ret_handles

    def update_list(self, mod_as, principal, mod_as_ihandle, group_ihandle=None):
        new_VS = VS() # a new VS to store into

        # Check to see if the principal is a group or user
        group = False
        if principal.is_group():
            group = True

        # If we don't have an entry for the mod_as, add one
        if mod_as not in self.vsl.keys():
            self.vsl[mod_as] = VS()

        # Find the most updated version list across all VS's by finding the VS with the
        # most recent version of each i-handle
        highest = -1
        best_vect = None

        for p in self.vsl.keys():
            vect = self.vsl[p]

            #sum the version numbers to find the aggregate amount of changes encapsulated
            # in the version vector
            total = sum(vect.v_vect.values())

            if total > highest:
                highest = total
                best_vect = vect.v_vect


        new_VS.ihandle = mod_as_ihandle
        new_VS.group_ihandle = self.vsl[mod_as].group_ihandle
        new_vector = best_vect

        # Check if this is our first time modifying this principal's itable
        if principal not in new_vector:
            new_vector[principal] = 0
        new_vector[principal] += 1

        if group:
            new_VS.group_ihandle[principal] = group_ihandle

        new_VS.v_vect = new_vector
        new_VS.user = mod_as

        self.update_VS(principal, new_VS)

### necessary packages for crypto-related functionality for
### this symmetric key store class
from cryptography.fernet import Fernet
import secfs.crypto
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend

class SymmetricKeyStore:
    def __init__(self, users, groups):
        """
        users: a dict mapping users -> public keys
        groups: a dict mapping groups -> list of users
        """
        # deserialize public key from PEM encoded data
        for u in users:
            users[u] = load_pem_public_key(users[u], backend=default_backend())

        # assign users keys
        self.users = {user: secfs.crypto.encrypt_asym(users[u], Fernet.generate_key()) for user in users}

        # assign groups keys
        self.groups = {}
        for group in groups:
            group_key = Fernet.generate_key()
            self.groups[group] = {user: secfs.crypto.encrypt_asym(users[user], group_key)
                                  for user in groups[group]}