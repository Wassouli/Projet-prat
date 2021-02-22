import torch
from utils.torch_utils import init_seed

from datasets.get_dataset import get_dataset
from models.get_model import get_model
from losses.get_loss import get_loss
from trainer.get_trainer import get_trainer
from utils.torch_utils import bias_parameters, weight_parameters, \
    load_checkpoint, save_checkpoint, AdamW

def main(cfg, _log):
    init_seed(cfg.seed)

    _log.info("=> fetching img pairs.")
    train_set, valid_set = get_dataset(cfg)

    _log.info('{} samples found, {} train samples and {} test samples '.format(
        len(valid_set) + len(train_set),
        len(train_set),
        len(valid_set)))

    train_loader = torch.utils.data.DataLoader(
        train_set, batch_size=cfg.train.batch_size,
        num_workers=cfg.train.workers, pin_memory=True, shuffle=True)

    max_test_batch = 4
    if type(valid_set) is torch.utils.data.ConcatDataset:
        valid_loader = [torch.utils.data.DataLoader(
            s, batch_size=min(max_test_batch, cfg.train.batch_size),
            num_workers=min(4, cfg.train.workers),
            pin_memory=True, shuffle=False) for s in valid_set.datasets]
        valid_size = sum([len(l) for l in valid_loader])
    else:
        valid_loader = torch.utils.data.DataLoader(
            valid_set, batch_size=min(max_test_batch, cfg.train.batch_size),
            num_workers=min(4, cfg.train.workers),
            pin_memory=True, shuffle=False)
        valid_size = len(valid_loader)

    if cfg.train.epoch_size == 0:
        cfg.train.epoch_size = len(train_loader)
    if cfg.train.valid_size == 0:
        cfg.train.valid_size = valid_size
    cfg.train.epoch_size = min(cfg.train.epoch_size, len(train_loader))
    cfg.train.valid_size = min(cfg.train.valid_size, valid_size)

    model = get_model(cfg.model)
    loss = get_loss(cfg.loss)
    trainer = get_trainer(cfg.trainer)(
        train_loader, valid_loader, model, loss, _log, cfg.save_root, cfg.train)
    
    for name, param in model.named_parameters():
      if("pyramid" in name)==False:
        param.requires_grad=False
          
      else:
        print(name,param.requires_grad) 
          #parameter.requires_grad = False
    epoch, weights = load_checkpoint(    'checkpoints/Sintel/pwclite_ar.tar')
    print("traiiiiiiiiiiiiiiiiiiiiiiiiiiiiin",weights)
 
    trainer.model=model
    trainer.train()
