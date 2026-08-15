create database bank_db;
use bank_db;
create table customers(customer_id int primary key auto_increment, username varchar(50) unique, password_hash varchar(256), email varchar(100), phone varchar(10), address text, account_number varchar(20) unique, balance float(10,2) default 0.00, created_at timestamp default current_timestamp);
alter table customers add column age varchar(2);
alter table customers add column gender char(1);
alter table customers add column DOB date;
alter table customers add column interest decimal(10,2);
alter table customers add column acc_holder varchar(20) not NULL;
alter table customers modify balance float(10,2) default 0.00;
alter table customers modify interest decimal(10,2) default 0.00;


desc customers;
alter table customers modify balance decimal(10,2);

create table admins( admin_id int primary key , username varchar(50) unique, password_hash varchar(255));
alter table admins modify admin_id int auto_increment;
desc admins;

create table transactions(transaction_id int primary key, customer_id int, transaction_type enum('Withdrawal', 'Transfer'), amount decimal(10,2), recipient_account varchar(20), transaction_date timestamp default current_timestamp, foreign key (customer_id) references customers(customer_id));
alter table transactions modify transaction_type enum('Credit','Debit');
alter table transactions add column interest decimal(10,2);
desc transactions;
alter table customers modify column gender char(10);


select * from transactions;
select * from admins;

desc customers;
alter table customers modify gender char(10);
select * from customers;
show tables;

 


