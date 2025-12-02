import React, { createContext } from 'react';

export const UserContext = createContext(null);

export function UserProvider({ children, value }) {
  const [userState, setUserState] = React.useState(null);

  // Use provided value or internal state
  const contextValue = value || { user: userState, setUser: setUserState };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
}
