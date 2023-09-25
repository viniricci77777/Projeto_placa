create database cadastros;

use cadastros;

# tabela pessoas
create table pessoas(
cpf bigint not null,
nome varchar(50) not null,
placa_automovel varchar(7) not null,
cargo enum('F', 'A') not null,
primary key(cpf)
)default charset utf8mb4;

INSERT INTO `pessoas` (`cpf`, `nome`, `placa_automovel`, `cargo`)
 VALUES 
 ('12345678900', 'João da Silva', 'ABC1234', 'F'),
 ('98765432100', 'Maria Santos', 'XYZ5678', 'A'),
 ('11122233344', 'Pedro Oliveira', 'DEF5678', 'A'),
 ('55566677788', 'Ana Pereira', 'GHI1234', 'A'),
 ('99900011122', 'Lucas Ferreira', 'JKL5678', 'F'),
 ('33344455566', 'Mariana Souza', 'MNO1234', 'F'),
 ('77788899900', 'Ricardo Almeida', 'PQR5678', 'F'),
 ('88899900011', 'Laura Costa', 'STU1234', 'A'),
 ('78496587599', 'leonardo neves bolfarini', 'FBR2A23', 'F'),
('44455566677', 'Eduardo Santos', 'VWX5678', 'A');

select * from pessoas;
