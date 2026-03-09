package com.unilopers.cinema.controller;

import com.unilopers.cinema.dto.request.CreateUsuarioDTO;
import com.unilopers.cinema.dto.request.LoginRequestDTO;
import com.unilopers.cinema.dto.response.AuthResponseDTO;
import com.unilopers.cinema.dto.response.UsuarioDTO;
import com.unilopers.cinema.mapper.UsuarioMapper;
import com.unilopers.cinema.model.Usuario;
import com.unilopers.cinema.repository.UsuarioRepository;
import com.unilopers.cinema.security.JwtTokenProvider;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
public class AuthController {

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Autowired
    private UsuarioMapper usuarioMapper;

    @PostMapping("/login")
    public ResponseEntity<AuthResponseDTO> login(@RequestBody LoginRequestDTO loginDTO) {
        try {
            UsernamePasswordAuthenticationToken authToken = 
                    new UsernamePasswordAuthenticationToken(loginDTO.getEmail(), loginDTO.getPassword());
            
            Authentication authentication = authenticationManager.authenticate(authToken);

            Usuario usuario = (Usuario) authentication.getPrincipal();

            String token = jwtTokenProvider.gerarToken(usuario);

            AuthResponseDTO responseDTO = new AuthResponseDTO(
                    token, 
                    usuario.getUsername(),
                    "Login realizado com sucesso"
            );

            return ResponseEntity.ok(responseDTO);
            
        } catch (AuthenticationException e) {
            return ResponseEntity.status(401).build();
        }
    }

    @PostMapping("/register")
    public ResponseEntity<UsuarioDTO> register(@RequestBody CreateUsuarioDTO createUsuarioDTO) {
        Usuario usuario = usuarioMapper.toEntity(createUsuarioDTO);
        usuario.setRoles("ROLE_USER");
        Usuario salvo = usuarioRepository.save(usuario);
        return ResponseEntity.ok(usuarioMapper.toDTO(salvo));
    }
}