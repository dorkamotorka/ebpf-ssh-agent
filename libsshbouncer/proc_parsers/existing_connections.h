#ifndef SSHBOUNCER_EXISTING_CONNECTIONS_H
#define SSHBOUNCER_EXISTING_CONNECTIONS_H

#include <stdint.h>
#include <string>
#include <vector>

namespace sshbouncer {

#define SSH_SESSION_UNKNOWN -1

struct ssh_session {
  int32_t pts_pid;
  int32_t ptm_pid;
  int32_t bash_pid;

  uint32_t client_port;
  uint32_t server_port;
  std::string client_ip;
  std::string server_ip;

  uint32_t user_id;

  uint64_t start_time;
};

class ExistingConnections {
public:
  ExistingConnections();
  virtual ~ExistingConnections();

  std::vector<struct ssh_session> get_sessions();

private:
  std::vector<struct ssh_session> sessions;
};

} // namespace sshbouncer
#endif /* SSHBOUNCER_EXISTING_CONNECTIONS_H */