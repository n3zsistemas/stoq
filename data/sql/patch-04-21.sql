-- Create a table for storing work order's history
CREATE TABLE work_order_history (
    id serial NOT NULL PRIMARY KEY,
    te_id bigint UNIQUE REFERENCES transaction_entry(id),

    date timestamp NOT NULL,
    what text NOT NULL,
    old_value text,
    new_value text,
    notes text,
    user_id bigint NOT NULL REFERENCES login_user(id) ON UPDATE CASCADE,
    work_order_id bigint NOT NULL REFERENCES work_order(id) ON UPDATE CASCADE
);

-- Add is_rejected flag on work_order
ALTER TABLE work_order
    ADD COLUMN is_rejected boolean NOT NULL DEFAULT false;
